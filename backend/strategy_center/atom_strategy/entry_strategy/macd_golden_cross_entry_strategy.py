from backend.strategy_center.atom_strategy.strategy_imports import *
# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = OKXTickerService()
tv = KlineDataCollector()

@registry.register(name="macd_golden_cross_entry_strategy",
                   desc="MACD黄金交叉买入策略",
                   side="long",
                   type="entry")
def macd_golden_cross_entry_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return macd_golden_cross_entry_strategy_backtest(df)
    else:
        return macd_golden_cross_entry_strategy_live(df, stIns)

def macd_golden_cross_entry_strategy_backtest(df: pd.DataFrame):
    # Initialize entry_sig and entry_price columns
    df['entry_sig'] = 0
    df['entry_price'] = 0
    
    # MACD calculation
    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # Create conditions for MACD golden cross buy signal
    condition = (
        (df['macd'].shift(1) < df['signal_line'].shift(1)) &  # Previous MACD was below signal line
        (df['macd'] > df['signal_line'])                       # Current MACD is above signal line
    )
    
    # Apply buy signals
    df.loc[condition, 'entry_sig'] = 1
    df.loc[condition, 'entry_price'] = df.loc[condition, 'close']
    
    # Drop temporary columns if needed and return
    df.drop(['ema12', 'ema26', 'macd', 'signal_line'], axis=1, inplace=True)
    return df

def macd_golden_cross_entry_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        df['signal'] = 'no_sig'
        
        # Calculate MACD and signal line for the latest data
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Check for MACD golden cross signal
        if (
            (df.iloc[-2]['macd'] < df.iloc[-2]['signal_line']) and
            (df.iloc[-1]['macd'] > df.iloc[-1]['signal_line'])
        ):
            df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value
        
        # Execute the signal
        if df.iloc[-1]['signal'] == EnumSide.BUY.value:
            if stIns.loss_per_trans is None or stIns.loss_per_trans <= 0:
                print("MACD Golden Cross Live Strategy: Invalid loss per transaction, no signal.")
                res.signal = False
                return res
            
            entry_price = df.iloc[-1]['close']
            stop_loss_price = entry_price * 0.98  # Example stop loss
            leverage = getattr(stIns, 'leverage', 3)
            max_loss_per_trade = stIns.loss_per_trans
            
            if pd.isna(entry_price) or pd.isna(stop_loss_price):
                print("MACD Golden Cross Live Strategy: Price data contains NaN, no signal.")
                res.signal = False
                return res
            
            position = StrategyUtils.calculate_position(entry_price, stop_loss_price, leverage, max_loss_per_trade)
            if position <= 0:
                print(f"MACD Golden Cross Live Strategy: Calculated position ({position}) is invalid, no signal.")
                res.signal = False
                return res
            
            try:
                res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=str(position))
                if not res.sz or res.sz == '0' or pd.isna(float(res.sz)):
                    print(f"MACD Golden Cross Live Strategy: Invalid sz ({res.sz}), no signal.")
                    res.signal = False
                    return res
            except Exception as e:
                print(f"MACD Golden Cross Live Strategy: Failed to get sz - {str(e)}, no signal.")
                res.signal = False
                return res
            
            res.signal = True
            res.side = EnumSide.BUY.value
            res.pos_side = EnumPosSide.LONG.value
            res.exit_price = str(df.iloc[-2]['close'])  # Example exit price
            res.interval = stIns.time_frame
            res.st_inst_id = stIns.id
            print(f"MACD Golden Cross Live Strategy: {stIns.trade_pair} position is: {position}")
            return res
        else:
            print("MACD Golden Cross Live Strategy: No signal.")
            res.signal = False
            return res