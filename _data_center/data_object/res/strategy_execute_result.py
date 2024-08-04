from pydantic import BaseModel
from typing import Optional


class StrategyExecuteResult:
    # 买入方向
    side: Optional[str] = None
    # 买入信号
    signal: Optional[bool] = False
    # 买入价格
    entryPrice: Optional[float] = -1.0
    # 止盈价格
    profitPrice: Optional[float] = -1.0
    # 止损价格
    lossPrice: Optional[float] = -1.0
    # 离场价格
    exitPrice: Optional[float] = -1.0
    # 买入仓位
    sz: Optional[float] = -1.0



