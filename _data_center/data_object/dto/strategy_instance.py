from pydantic import BaseModel, dataclasses
from typing import Optional
from datetime import datetime

from _data_center.data_object.enum_obj import EnumTradeEnv


# 策略实例
class StrategyInstance(BaseModel):
    id: Optional[int] = None
    # 交易对 eg.BTC-USDT
    tradePair: str
    # 每次下单数量，整数 eg.1000
    # position: int = 0
    # 允许交易方向
    side: str = "all"
    # 每笔交易损失
    lossPerTrans: int = 0
    # 实例已成交的订单数量
    positionCount: int = 0
    # 时间窗口 eg.1D, 4H
    timeFrame: str
    # 订单信息
    orderInfo: str = ""
    # 买入价格
    entryPrice: Optional[float] = -1.0
    # 买入策略id
    stEntryCode: str
    # 卖出策略id
    stExitCode: str
    # 策略实例开关
    switch: int = 1
    # 删除
    delete: int = 0
    # 实盘虚拟盘
    flag: Optional[str] = "0"
    # 创建时间
    gmtCreate: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新时间
    gmtUpdate: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 是否实盘
    env: str = EnumTradeEnv.DEMO.value
