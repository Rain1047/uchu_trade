from typing import Optional

from pydantic import BaseModel


class StopLossReq(BaseModel):
    instId: Optional[str] = ''
    # 止损类型：固定止损、移动止损
    slType: Optional[str] = ''
    # 止损价格
    slPx: Optional[str] = ''
    # 止损触发价类型：最新价、最优价
    slTriggerPxType: Optional[str] = ''
    # 止损触发价
    slTriggerPx: Optional[str] = ''

