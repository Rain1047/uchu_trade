from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from sqlalchemy import select

from backend.data_center.data_object.enum_obj import EnumTradeEnv


# 策略实例
class StrategyInstance(BaseModel):
    id: Optional[int] = None
    # 交易对 eg.BTC-USDT
    trade_pair: str
    # 允许交易方向
    side: str
    # 每笔交易损失
    loss_per_trans: Optional[int] = 0
    # 每次下单数量，整数 eg.1000
    entry_per_trans: Optional[int] = 0

    # 时间窗口 eg.1D, 4H
    time_frame: str

    # 买入策略code
    entry_st_code: str
    # 卖出策略code
    exit_st_code: str
    # 过滤策略code
    filter_st_code: str
    # 策略实例开关
    switch: int = 1
    # 删除
    delete: int = 0
    # 实盘虚拟盘
    flag: Optional[str] = "0"
    # 是否实盘
    env: str = EnumTradeEnv.DEMO.value

    # 实例已成交的订单数量
    positionCount: Optional[int] = 0
    # 订单信息
    orderInfo: str = ""
    # 买入价格
    entryPrice: Optional[float] = -1.0
    # 创建时间
    gmtCreate: str = datetime.now()
    # 更新时间
    gmtUpdate: str = datetime.now()

    @classmethod
    def get_by_id(cls, id: int):
        stmt = select(cls).where(cls.id == id, cls.delete == 0)
        return session.execute(stmt).scalar_one_or_none()



