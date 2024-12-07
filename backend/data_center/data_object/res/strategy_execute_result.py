from pydantic import BaseModel
from typing import Optional


class StrategyExecuteResult:
    #
    symbol: str
    # 买入方向
    side: Optional[str] = None
    # 买入信号
    signal: Optional[bool] = False
    # 买入价格
    entry_price: Optional[str] = ''
    # 止盈价格
    profit_price: Optional[str] = ''
    # 止损价格
    stop_loss_price: Optional[str] = ''
    # 离场价格
    exit_price: Optional[str] = ''
    # 买入仓位
    sz: Optional[str] = ''



