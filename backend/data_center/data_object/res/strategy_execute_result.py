from pydantic import BaseModel
from typing import Optional


class StrategyExecuteResult:
    # 交易对
    symbol: str
    # 买入方向
    side: Optional[str] = None
    # 持仓方向
    pos_side: Optional[str] = None
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
    # USDT仓位
    sz_usdt: Optional[str] = ''
    # 交易实例id
    st_inst_id: int
    # 交易间隔
    interval: Optional[str] = ''
    # 策略实例id




