from backend.strategy_center.atom_strategy.strategy_imports import *
# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = OKXTickerService()
tv = KlineDataCollector()

@registry.register(name="sma_cross_strategy", desc="SMA10 and SMA20 Cross Strategy", side="both", type="entry_exit")
def sma_cross_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return sma_cross_strategy_backtest(df)
    else:
        return sma_cross_strategy_live(df, stIns)

def sma_cross_strategy_backtest(df: pd.DataFrame):
    # Initialize signal columns
    df['entry_sig'] = 0
    df['entry_price'] = 0
    df['exit_sig'] = 0
    df['exit_price'] = 0

    # Calculate SMAs
    df['SMA10'] = df['close'].rolling(window=10).mean()
    df['SMA20'] = df['close'].rolling(window=20).mean()

    # Create conditions for signals
    buy_condition = (df['SMA10'].shift(1) < df['SMA20'].shift(1)) & (df['SMA10'] > df['SMA20'])
    sell_condition = (df['SMA10'].shift(1) > df['SMA20'].shift(1)) & (df['SMA10'] < df['SMA20'])

    # Debug information
    df['debug_buy_condition'] = buy_condition
    df['debug_sell_condition'] = sell_condition

    # Set buy signals
    df.loc[buy_condition, 'entry_sig'] = 1
    df.loc[buy_condition, 'entry_price'] = df.loc[buy_condition, 'close']

    # Set sell signals
    df.loc[sell_condition, 'exit_sig'] = 1
    df.loc[sell_condition, 'exit_price'] = df.loc[sell_condition, 'close']

    # Clean up temporary columns
    df.drop(['debug_buy_condition', 'debug_sell_condition'], axis=1, inplace=True)

    return df

def sma_cross_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        df['signal'] = 'no_sig'
        
        # Calculate SMAs for the most recent data
        if len(df) >= 20:  # Ensure enough data for 20 periods
            df['SMA10'] = df['close'].rolling(window=10).mean()
            df['SMA20'] = df['close'].rolling(window=20).mean()
            
            # Check for buy signal
            if df.iloc[-2]['SMA10'] < df.iloc[-2]['SMA20'] and df.iloc[-1]['SMA10'] > df.iloc[-1]['SMA20']:
                df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value

            # Check for sell signal
            elif df.iloc[-2]['SMA10'] > df.iloc[-2]['SMA20'] and df.iloc[-1]['SMA10'] < df.iloc[-1]['SMA20']:
                df.loc[df.index[-1], 'signal'] = EnumSide.SELL.value

            # If buy signal is generated
            if df.iloc[-1]['signal'] == EnumSide.BUY.value:
                return process_signal(df, stIns, res, EnumSide.BUY)
            
            # If sell signal is generated
            elif df.iloc[-1]['signal'] == EnumSide.SELL.value:
                return process_signal(df, stIns, res, EnumSide.SELL)
    
    print("sma_cross_strategy_live#execute result: no signal")
    res.signal = False
    return res

def process_signal(df, stIns, res, side):
    # Check if loss_per_trans is valid
    if stIns.loss_per_trans is None or stIns.loss_per_trans <= 0:
        print(f"sma_cross_strategy_live#execute result: loss_per_trans ({stIns.loss_per_trans}) is invalid, no signal")
        res.signal = False
        return res

    # Check if price data is valid
    entry_price = df.iloc[-1]['close']
    stop_loss_price = entry_price * 0.98  # Example stop loss, can be changed
    leverage = getattr(stIns, 'leverage', 3)  # Default leverage is 3 if not provided
    
    if pd.isna(entry_price) or pd.isna(stop_loss_price):
        print(f"sma_cross_strategy_live#execute result: price data contains NaN, no signal")
        res.signal = False
        return res

    # Position calculation
    position = StrategyUtils.calculate_position(entry_price, stop_loss_price, leverage, stIns.loss_per_trans)
    if position <= 0:
        print(f"sma_cross_strategy_live#execute result: calculated position ({position}) is invalid, no signal")
        res.signal = False
        return res
    
    try:
        res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=str(position))
        if not res.sz or res.sz == '0' or pd.isna(float(res.sz)):
            print(f"sma_cross_strategy_live#execute result: sz ({res.sz}) is invalid, no signal")
            res.signal = False
            return res
    except Exception as e:
        print(f"sma_cross_strategy_live#execute result: get_sz failed: {str(e)}, no signal")
        res.signal = False
        return res
    
    # Package the result
    res.signal = True
    res.side = side.value
    res.pos_side = EnumPosSide.LONG.value if side == EnumSide.BUY else EnumPosSide.SHORT.value
    res.exit_price = str(df.iloc[-2]['SMA20'])
    res.interval = stIns.time_frame
    res.st_inst_id = stIns.id
    print(f"sma_cross_strategy_live#execute result: {stIns.trade_pair} position is: {position}")
    return res