import os
import sys

# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import talib
from backend._data_center.data_object.dto.strategy_instance import StrategyInstance
from backend._data_center.data_object.enum_obj import *
from backend._service.data_api import query_candles_with_time_frame
import okx.PublicData as PublicData
import okx.MarketData as MarketData

marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)

publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)


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
    df = query_candles_with_time_frame(stIns.tradePair, stIns.flag, stIns.timeFrame)

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
                stIns.lossPerTrans * round(df.iloc[-1]['close'] / (df.iloc[-1]['close'] - df.iloc[-1]['middle_band']),
                                           2) * 10)
            print(f"{stIns.tradePair} position is: {position}")

            # 获取单个产品行情信息
            res.sz = get_sz(stIns, position)
            print(f"{stIns.tradePair} sz is: {res.sz}")
            res.signal = True
            res.side = EnumSide.BUY.value
            res = get_exit_price(df, res)
            return res

        elif df.iloc[-1]['signal'] == EnumSide.SELL.value:
            # 获取仓位
            position = str(
                stIns.lossPerTrans * round(df.iloc[-1]['close'] / (df.iloc[-1]['middle_band'] - df.iloc[-1]['close']),
                                           2) * 10 * (-1))
            res.sz = get_sz(stIns, position)
            res.signal = True
            res.side = EnumSide.BUY.value
            res.exitPrice = df.iloc[-1]['middle_band'] * 1.3
            return res

        else:
            res.sz = 100
            res.signal = False
            return res


# 获取张数
def get_sz(stIns: StrategyInstance, position: str):
    # 获取单个产品行情信息
    last_price = marketDataAPI.get_ticker(
        instId=stIns.tradePair
    )['data'][0]['last']

    # 张币转换
    sz = publicDataAPI.get_convert_contract_coin(
        instId=stIns.tradePair,
        px=last_price,
        sz=position,
        unit=EnumUnit.USDS.value
    )['data'][0]['sz']
    return sz


def get_exit_price(df, res: StrategyExecuteResult) -> StrategyExecuteResult:
    if df.iloc[-1]['signal'] == EnumSide.BUY.value:
        res.exitPrice = df.iloc[-2]['middle_band']
        if df.iloc[-1]['close'] > df.iloc[-1]['upper_band2']:
            res.profitPrice = df.iloc[-1]['upper_band1']
    elif df.iloc[-1]['signal'] == EnumSide.SELL.value:
        res.exitPrice = df.iloc[-1]['middle_band']
        if df.iloc[-1]['close'] < df.iloc[-1]['lower_band2']:
            res.profitPrice = df.iloc[-1]['lower_band1']
    return res
