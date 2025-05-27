from backend.strategy_center.atom_strategy.strategy_imports import *
# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = OKXTickerService()
tv = KlineDataCollector()

@registry.register(name="sma_cross_entry_long_strategy", desc="SMA交叉买入策略", side="long", type="entry")
def sma_cross_entry_long_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return sma_cross_entry_long_strategy_backtest(df)
    else:
        return sma_cross_entry_long_strategy_live(df, stIns)

def sma_cross_entry_long_strategy_backtest(df: pd.DataFrame):
    # Calculate SMA10 and SMA30
    df['SMA10'] = df['close'].rolling(window=10).mean()
    df['SMA30'] = df['close'].rolling(window=30).mean()
    
    # Initialize buy signal column with zeros
    df['entry_sig'] = 0
    df['entry_price'] = 0
    
    # Create conditions for the SMA cross
    current_condition = (
        (df['SMA10'].shift(1) < df['SMA30'].shift(1)) &  # Previous SMA10 < SMA30
        (df['SMA10'] > df['SMA30'])                      # Current SMA10 > SMA30
    )
    
    # Assign signals and entry prices
    df.loc[current_condition, 'entry_sig'] = 1
    df.loc[current_condition, 'entry_price'] = df.loc[current_condition, 'close']
    
    return df

def sma_cross_entry_long_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        # Calculate SMA10 and SMA30
        df['SMA10'] = df['close'].rolling(window=10).mean()
        df['SMA30'] = df['close'].rolling(window=30).mean()
        df['signal'] = 'no_sig'
        
        # Check for SMA cross from the last two prices
        if ((df.iloc[-2]['SMA10'] > df.iloc[-2]['SMA30']) and
                (df.iloc[-3]['SMA10'] < df.iloc[-3]['SMA30'])):
            df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value
        
        # Set trading signal if buy signal is detected
        if df.iloc[-1]['signal'] == EnumSide.BUY.value:
            if stIns.loss_per_trans is None or stIns.loss_per_trans <= 0:
                print(f"sma_cross_entry_long_strategy_live#execute result: loss_per_trans ({stIns.loss_per_trans}) is invalid, no signal")
                res.signal = False
                return res
            
            entry_price = df.iloc[-1]['close']
            stop_loss_price = df.iloc[-1]['SMA30'] if 'SMA30' in df.columns else entry_price * 0.98
            leverage = getattr(stIns, 'leverage', 3)
            max_loss_per_trade = stIns.loss_per_trans
            if pd.isna(entry_price) or pd.isna(stop_loss_price):
                print(f"sma_cross_entry_long_strategy_live#execute result: price data contains NaN, no signal")
                res.signal = False
                return res
            
            position = StrategyUtils.calculate_position(entry_price, stop_loss_price, leverage, max_loss_per_trade)
            if position <= 0:
                print(f"sma_cross_entry_long_strategy_live#execute result: calculated position ({position}) is invalid, no signal")
                res.signal = False
                return res
            
            try:
                res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=str(position))
                if not res.sz or res.sz == '0' or pd.isna(float(res.sz)):
                    print(f"sma_cross_entry_long_strategy_live#execute result: sz ({res.sz}) is invalid, no signal")
                    res.signal = False
                    return res
            except Exception as e:
                print(f"sma_cross_entry_long_strategy_live#execute result: get_sz failed: {str(e)}, no signal")
                res.signal = False
                return res
            
            res.signal = True
            res.side = EnumSide.BUY.value
            res.pos_side = EnumPosSide.LONG.value
            res.exit_price = str(df.iloc[-2]['SMA30'])
            res.interval = stIns.time_frame
            res.st_inst_id = stIns.id
            print(f"sma_cross_entry_long_strategy_live#execute result: {stIns.trade_pair} position is: {position}")
            return res
        else:
            print("sma_cross_entry_long_strategy_live#execute result: no signal")
            res.signal = False
            return res