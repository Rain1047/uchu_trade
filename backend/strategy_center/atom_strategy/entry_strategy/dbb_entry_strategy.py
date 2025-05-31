from backend.strategy_center.atom_strategy.strategy_imports import *
from backend.strategy_center.atom_strategy.strategy_utils import StrategyUtils

# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = OKXTickerService()
tv = KlineDataCollector()


@registry.register(name="dbb_entry_long_strategy", desc="布林带入场策略", side="long", type="entry")
def dbb_entry_long_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return dbb_entry_long_strategy_backtest(df)
    else:
        return dbb_entry_long_strategy_live(df, stIns)


def dbb_entry_long_strategy_backtest(df: pd.DataFrame):
    # 如果缺少布林带列则即时计算（period=20, 2σ）
    if 'upper_band1' not in df.columns or 'upper_band2' not in df.columns:
        sma20 = df['close'].rolling(window=20).mean()
        std20 = df['close'].rolling(window=20).std()
        df['upper_band1'] = sma20 + std20 * 2
        df['upper_band2'] = sma20 + std20 * 3

    # Initialize buy_sig column with zeros
    df['entry_sig'] = 0
    df['entry_price'] = 0
    df['prev_open_1'] = df['open'].shift(1)
    df['prev_upper_band1_1'] = df['upper_band1'].shift(1)
    # Create conditions for current row
    current_condition = (
            (df['open'] < df['upper_band1'])  # 条件1
            & (df['close'] > df['upper_band1'])  # 条件2
            & (df['prev_open_1'] < df['prev_upper_band1_1'])  # 条件3
    )

    # 添加调试信息
    df['debug_condition1'] = df['open'] < df['upper_band1']
    df['debug_condition2'] = df['close'] > df['upper_band1']
    df['debug_condition3'] = df['prev_open_1'] < df['prev_upper_band1_1']

    # Set buy signals
    df.loc[current_condition, 'entry_sig'] = 1
    df.loc[current_condition, 'entry_price'] = df.loc[current_condition, 'close']
    # Clean up temporary columns
    df.drop(['prev_open_1', 'prev_upper_band1_1',
             'debug_condition1', 'debug_condition2',
             'debug_condition3'], axis=1, inplace=True, errors='ignore')

    return df


def dbb_entry_long_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        df['signal'] = 'no_sig'
        if ((df.iloc[-2]['close'] > df.iloc[-2]['upper_band1']) and
                (df.iloc[-3]['close'] < df.iloc[-3]['upper_band1']) and
                (df.iloc[-4]['close'] < df.iloc[-4]['upper_band1'])):
            df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value
        # 如果满足买入信号，则设置交易信号为True
        if df.iloc[-1]['signal'] == EnumSide.BUY.value:
            # 检查loss_per_trans是否有效
            if stIns.loss_per_trans is None or stIns.loss_per_trans <= 0:
                print(f"dbb_entry_long_strategy_live#execute result: loss_per_trans ({stIns.loss_per_trans}) is invalid, no signal")
                res.signal = False
                return res
            
            # 检查价格数据是否有效
            entry_price = df.iloc[-1]['close']
            # 止损价可根据实际策略调整，这里用sma20
            stop_loss_price = df.iloc[-1]['sma20'] if 'sma20' in df.columns else entry_price * 0.98
            leverage = getattr(stIns, 'leverage', 3)  # 优先取stIns.leverage，否则默认3倍杠杆
            max_loss_per_trade = stIns.loss_per_trans
            
            if pd.isna(entry_price) or pd.isna(stop_loss_price):
                print(f"dbb_entry_long_strategy_live#execute result: price data contains NaN, no signal")
                res.signal = False
                return res
            
            # 仓位计算
            position = StrategyUtils.calculate_position(entry_price, stop_loss_price, leverage, max_loss_per_trade)
            if position <= 0:
                print(f"dbb_entry_long_strategy_live#execute result: calculated position ({position}) is invalid, no signal")
                res.signal = False
                return res
            
            # 获取单个产品行情信息
            try:
                res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=str(position))
                # 检查sz是否有效
                if not res.sz or res.sz == '0' or pd.isna(float(res.sz)):
                    print(f"dbb_entry_long_strategy_live#execute result: sz ({res.sz}) is invalid, no signal")
                    res.signal = False
                    return res
            except Exception as e:
                print(f"dbb_entry_long_strategy_live#execute result: get_sz failed: {str(e)}, no signal")
                res.signal = False
                return res
            
            # 封装结果
            res.signal = True
            res.side = EnumSide.BUY.value
            res.pos_side = EnumPosSide.LONG.value
            res.exit_price = str(df.iloc[-2]['sma20'])
            res.interval = stIns.time_frame
            res.st_inst_id = stIns.id
            print(f"dbb_entry_long_strategy_live#execute result: {stIns.trade_pair} position is: {position}")
            return res
        else:
            print("dbb_entry_long_strategy_live#execute result: no signal")
            res.signal = False
            return res


if __name__ == '__main__':
    print(registry.list_strategies())
