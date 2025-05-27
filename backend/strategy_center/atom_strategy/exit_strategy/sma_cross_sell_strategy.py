from backend.strategy_center.atom_strategy.strategy_imports import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = OKXTickerService()
tv = KlineDataCollector()

@registry.register(name="sma_cross_sell_strategy", desc="SMA10低于SMA30卖出策略", side="short", type="exit")
def sma_cross_sell_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return sma_cross_sell_strategy_backtest(df)
    else:
        return sma_cross_sell_strategy_live(df, stIns)

def sma_cross_sell_strategy_backtest(df: pd.DataFrame):
    # 计算SMA10和SMA30
    df['SMA10'] = df['close'].rolling(window=10).mean()
    df['SMA30'] = df['close'].rolling(window=30).mean()

    # 初始化卖出信号和价格
    df['exit_sig'] = 0
    df['exit_price'] = 0

    # 条件：SMA10从上方穿过SMA30
    current_condition = (df['SMA10'].shift(1) >= df['SMA30'].shift(1)) & (df['SMA10'] < df['SMA30'])

    # 设置卖出信号
    df.loc[current_condition, 'exit_sig'] = 1
    df.loc[current_condition, 'exit_price'] = df.loc[current_condition, 'close']

    # 返回
    return df

def sma_cross_sell_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        df['signal'] = 'no_sig'
        if ((df.iloc[-2]['SMA10'] < df.iloc[-2]['SMA30']) and
                (df.iloc[-3]['SMA10'] >= df.iloc[-3]['SMA30'])):
            df.loc[df.index[-1], 'signal'] = EnumSide.SELL.value
        
        if df.iloc[-1]['signal'] == EnumSide.SELL.value:
            if stIns.loss_per_trans is None or stIns.loss_per_trans <= 0:
                print(f"sma_cross_sell_strategy_live#execute result: loss_per_trans ({stIns.loss_per_trans}) is invalid, no signal")
                res.signal = False
                return res
            
            entry_price = df.iloc[-1]['close']
            stop_loss_price = df.iloc[-1]['SMA30'] if 'SMA30' in df.columns else entry_price * 1.02
            leverage = getattr(stIns, 'leverage', 3)
            max_loss_per_trade = stIns.loss_per_trans
            
            if pd.isna(entry_price) or pd.isna(stop_loss_price):
                print(f"sma_cross_sell_strategy_live#execute result: price data contains NaN, no signal")
                res.signal = False
                return res
            
            position = StrategyUtils.calculate_position(entry_price, stop_loss_price, leverage, max_loss_per_trade)
            if position <= 0:
                print(f"sma_cross_sell_strategy_live#execute result: calculated position ({position}) is invalid, no signal")
                res.signal = False
                return res
            
            try:
                res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=str(position))
                if not res.sz or res.sz == '0' or pd.isna(float(res.sz)):
                    print(f"sma_cross_sell_strategy_live#execute result: sz ({res.sz}) is invalid, no signal")
                    res.signal = False
                    return res
            except Exception as e:
                print(f"sma_cross_sell_strategy_live#execute result: get_sz failed: {str(e)}, no signal")
                res.signal = False
                return res
            
            res.signal = True
            res.side = EnumSide.SELL.value
            res.pos_side = EnumPosSide.SHORT.value
            res.exit_price = str(df.iloc[-2]['SMA30'])
            res.interval = stIns.time_frame
            res.st_inst_id = stIns.id
            print(f"sma_cross_sell_strategy_live#execute result: {stIns.trade_pair} position is: {position}")
            return res
        else:
            print("sma_cross_sell_strategy_live#execute result: no signal")
            res.signal = False
            return res