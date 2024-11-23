import os
import sys

import pandas as pd
from pandas import DataFrame
from tvDatafeed import Interval

from backend.data_center.data_gather.ticker_price_collector import TickerPriceCollector
from backend.data_center.data_object.enum_obj import EnumTradeType, EnumSide
from backend.data_center.data_object.res.strategy_execute_result import StrategyExecuteResult
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector

# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import talib
from backend.data_center.data_object.dto.strategy_instance import StrategyInstance
import okx.PublicData as PublicData
import okx.MarketData as MarketData
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper

marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)

publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)

okx = OKXAPIWrapper()

price_collector = TickerPriceCollector()


def dbb_entry_strategy_for_backtest(df: DataFrame) -> DataFrame:
    # if not df.empty:
    #     df['entry_sig'] = 0
    #     df['prev_close'] = df['close'].shift(1)
    #     df['prev_open'] = df['open'].shift(1)
    #     buy_mask1 = (df['open'] < df['upper_band1']) & \
    #                 (df['close'] > df['upper_band1']) & \
    #                 (df['close'] < df['upper_band2'])
    #     buy_mask2 = (df['prev_open'] < df['upper_band1']) & \
    #                 (df['prev_close'] < df['upper_band1'])
    #     final_buy_mask = buy_mask1 & buy_mask2
    #
    #     df.loc[final_buy_mask, 'entry_sig'] = 1
    #     # 使用实际收盘价作为入场价格
    #     df.loc[final_buy_mask, 'entry_price'] = df.loc[buy_mask1, 'open']
    # return df

    # Initialize buy_sig column with zeros
    df['entry_sig'] = 0

    # Create shifted columns
    df['prev_open_1'] = df['open'].shift(1)
    df['prev_open_2'] = df['open'].shift(2)
    df['prev_upper_band1_1'] = df['upper_band1'].shift(1)
    df['prev_upper_band1_2'] = df['upper_band1'].shift(2)

    # Create conditions for current row
    current_condition = (
            (df['open'] < df['upper_band1'])  # 条件1
            & (df['close'] > df['upper_band1'])  # 条件2
            & (df['prev_open_1'] < df['prev_upper_band1_1'])  # 条件3
            & (df['prev_open_2'] < df['prev_upper_band1_2'])  # 条件4
    )

    # 添加调试信息
    df['debug_condition1'] = df['open'] < df['upper_band1']
    df['debug_condition2'] = df['close'] > df['upper_band1']
    df['debug_condition3'] = df['prev_open_1'] < df['prev_upper_band1_1']
    df['debug_condition4'] = df['prev_open_2'] < df['prev_upper_band1_2']

    # Set buy signals
    df.loc[current_condition, 'entry_sig'] = 1

    # 验证信号
    problematic_signals = df[df['entry_sig'] == 1]
    if len(problematic_signals) > 0:
        print("\nSignal Verification:")
        for idx in problematic_signals.index:
            print(f"\nTime: {problematic_signals.loc[idx, 'datetime']}")
            print(f"Condition 1 (current open < upper_band1): {problematic_signals.loc[idx, 'debug_condition1']}")
            print(f"Condition 2 (current close > upper_band1): {problematic_signals.loc[idx, 'debug_condition2']}")
            print(f"Condition 3 (prev open < prev upper_band1): {problematic_signals.loc[idx, 'debug_condition3']}")
            print(f"Condition 4 (prev_2 open < prev_2 upper_band1): {problematic_signals.loc[idx, 'debug_condition4']}")

    # Clean up temporary columns
    df.drop(['prev_open_1', 'prev_open_2', 'prev_upper_band1_1',
             'prev_upper_band1_2', 'debug_condition1', 'debug_condition2',
             'debug_condition3', 'debug_condition4'], axis=1, inplace=True)

    return df


def dbb_strategy(stIns: StrategyInstance) -> StrategyExecuteResult:
    """
    双布林带突破策略：在股价突破双布林带上轨时执行买入操作。

    Args:
        stIns (StrategyInstance): 策略实例对象，包含交易对、时间窗口大小等信息。

    Returns:
        StrategyExecuteResult: 策略执行结果对象，包含交易信号和交易方向。
    """
    # 查询历史蜡烛图数据
    print("Double Bollinger Bands Strategy Start...")
    df = price_collector.query_candles_with_time_frame(stIns.trade_pair, stIns.time_frame)

    # 初始化策略执行结果对象
    res = StrategyExecuteResult()
    res.side = EnumSide.BUY.value

    # 检查 DataFrame 是否为空
    if not df.empty:
        # 计算布林带
        df['upper_band1'], df['middle_band'], df['lower_band1'] = talib.BBANDS(df['close'], timeperiod=20, nbdevup=1,
                                                                               nbdevdn=1)
        df['upper_band2'], _, df['lower_band2'] = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)

        df['signal'] = 'no_sig'
        # 实施交易策略
        print(f"{df.iloc[-2]['timestamp']},{df.iloc[-2]['close']},{df.iloc[-2]['upper_band1']},{df.iloc[-3]['close']}")

        if ((df.iloc[-2]['close'] > df.iloc[-2]['upper_band1']) and
                (df.iloc[-3]['close'] < df.iloc[-3]['upper_band1']) and
                (df.iloc[-4]['close'] < df.iloc[-4]['upper_band1'])):
            df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value

        if ((df.iloc[-1]['close'] < df.iloc[-1]['upper_band1']) and
                (df.iloc[-2]['close'] > df.iloc[-1]['upper_band1']) and
                (df.iloc[-3]['close'] > df.iloc[-3]['upper_band1'])):
            df.iloc[-1]['signal'] = EnumSide.SELL.value

        print(df.iloc[-1]['signal'])

        # 如果满足买入信号，则设置交易信号为True
        if df.iloc[-1]['signal'] == EnumSide.BUY.value and stIns.side in [EnumSide.BUY.value, EnumSide.ALL.value]:
            # 获取仓位
            position = str(
                stIns.loss_per_trans * round(df.iloc[-1]['close'] / (df.iloc[-1]['close'] - df.iloc[-1]['middle_band']),
                                             2) * 10)
            print(f"{stIns.trade_pair} position is: {position}")

            # 获取单个产品行情信息
            res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=position)
            print(f"{stIns.trade_pair} sz is: {res.sz}")
            res.signal = True
            res.side = EnumSide.BUY.value
            res = get_exit_price(df, res)
            return res

        elif df.iloc[-1]['signal'] == EnumSide.SELL.value:
            # 获取仓位
            position = str(
                stIns.loss_per_trans * round(df.iloc[-1]['close'] / (df.iloc[-1]['middle_band'] - df.iloc[-1]['close']),
                                             2) * 10 * (-1))
            res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=position)
            res.signal = True
            res.side = EnumSide.BUY.value
            res.exitPrice = str(df.iloc[-1]['middle_band'] * 1.3)
            return res
        else:
            res.signal = False
            return res


def get_exit_price(df, res: StrategyExecuteResult) -> StrategyExecuteResult:
    if df.iloc[-1]['signal'] == EnumSide.BUY.value:
        res.exitPrice = str(df.iloc[-2]['middle_band'])
        if df.iloc[-1]['close'] > df.iloc[-1]['upper_band2']:
            res.profitPrice = str(df.iloc[-1]['upper_band1'])
    elif df.iloc[-1]['signal'] == EnumSide.SELL.value:
        res.exitPrice = str(df.iloc[-1]['middle_band'])
        if df.iloc[-1]['close'] < df.iloc[-1]['lower_band2']:
            res.profitPrice = str(df.iloc[-1]['lower_band1'])
    return res


if __name__ == '__main__':
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_daily)
    df = pd.read_csv(f"{file_abspath}")

    df = dbb_entry_strategy_for_backtest(df)
