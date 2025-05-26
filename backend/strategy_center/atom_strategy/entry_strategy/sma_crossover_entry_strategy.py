from backend.strategy_center.atom_strategy.strategy_imports import *
# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = OKXTickerService()
tv = KlineDataCollector()

@registry.register(name="sma_crossover_entry_strategy", desc="SMA10穿过SMA50入场策略", side="long", type="entry")
def sma_crossover_entry_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return sma_crossover_entry_strategy_backtest(df)
    else:
        return sma_crossover_entry_strategy_live(df, stIns)

def sma_crossover_entry_strategy_backtest(df: pd.DataFrame):
    # 计算SMA10和SMA50
    df['sma10'] = df['close'].rolling(window=10).mean()
    df['sma50'] = df['close'].rolling(window=50).mean()

    # 初始化信号列
    df['entry_sig'] = 0
    df['entry_price'] = 0

    # 创建条件用于交叉信号
    cross_up = (df['sma10'] > df['sma50']) & (df['sma10'].shift(1) <= df['sma50'].shift(1))

    # 添加调试信息
    df['debug_cross_up'] = cross_up

    # 设置入场信号
    df.loc[cross_up, 'entry_sig'] = 1
    df.loc[cross_up, 'entry_price'] = df['close']

    # 清理临时列，debug信息可以根据需要保留或去掉
    df.drop(['debug_cross_up'], axis=1, inplace=True)

    return df

def sma_crossover_entry_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        # 计算SMA10和SMA50
        df['sma10'] = df['close'].rolling(window=10).mean()
        df['sma50'] = df['close'].rolling(window=50).mean()

        df['signal'] = 'no_sig'
        if (df.iloc[-2]['sma10'] > df.iloc[-2]['sma50']) and (df.iloc[-3]['sma10'] <= df.iloc[-3]['sma50']):
            df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value
            
        if df.iloc[-1]['signal'] == EnumSide.BUY.value:
            if stIns.loss_per_trans is None or stIns.loss_per_trans <= 0:
                print(f"sma_crossover_entry_strategy_live#execute result: loss_per_trans ({stIns.loss_per_trans}) is invalid, no signal")
                res.signal = False
                return res
            
            entry_price = df.iloc[-1]['close']
            stop_loss_price = df.iloc[-1]['sma50'] if 'sma50' in df.columns else entry_price * 0.98
            leverage = getattr(stIns, 'leverage', 3)
            max_loss_per_trade = stIns.loss_per_trans
            
            if pd.isna(entry_price) or pd.isna(stop_loss_price):
                print(f"sma_crossover_entry_strategy_live#execute result: price data contains NaN, no signal")
                res.signal = False
                return res

            position = StrategyUtils.calculate_position(entry_price, stop_loss_price, leverage, max_loss_per_trade)
            if position <= 0:
                print(f"sma_crossover_entry_strategy_live#execute result: calculated position ({position}) is invalid, no signal")
                res.signal = False
                return res
            
            try:
                res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=str(position))
                if not res.sz or res.sz == '0' or pd.isna(float(res.sz)):
                    print(f"sma_crossover_entry_strategy_live#execute result: sz ({res.sz}) is invalid, no signal")
                    res.signal = False
                    return res
            except Exception as e:
                print(f"sma_crossover_entry_strategy_live#execute result: get_sz failed: {str(e)}, no signal")
                res.signal = False
                return res
            
            res.signal = True
            res.side = EnumSide.BUY.value
            res.pos_side = EnumPosSide.LONG.value
            res.exit_price = str(df.iloc[-2]['sma50'])
            res.interval = stIns.time_frame
            res.st_inst_id = stIns.id
            print(f"sma_crossover_entry_strategy_live#execute result: {stIns.trade_pair} position is: {position}")
            return res
        else:
            print("sma_crossover_entry_strategy_live#execute result: no signal")
            res.signal = False
            return res