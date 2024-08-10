from typing import Optional

from pydantic import BaseModel


class StopLossReq(BaseModel):
    # 止损类型：固定止损、移动止损
    slType: Optional[str] = None
    # 止损价格
    slPx: Optional[str] = None
    # 止损触发价类型：最新价、最优价
    slTriggerPxType: Optional[str] = None
    # 止损触发价
    slTriggerPx: Optional[str] = None

