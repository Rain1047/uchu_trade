from pydantic import BaseModel
from typing import Optional


class StrategyExecuteResult:
    # 买入方向
    side: Optional[str] = None
    # 买入信号
    signal: Optional[bool] = False
    # 买入价格
    entryPrice: Optional[str] = ''
    # 止盈价格
    profitPrice: Optional[str] = ''
    # 止损价格
    lossPrice: Optional[str] = ''
    # 离场价格
    exitPrice: Optional[str] = ''
    # 买入仓位
    sz: Optional[str] = ''



