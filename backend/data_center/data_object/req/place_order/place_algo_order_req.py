from typing import Optional
from pydantic import BaseModel

from backend.data_center.data_object.enum_obj import *


class PostAlgoOrderReq(BaseModel):
    """
    下单请求参数
    """
    # 基础参数
    instId: str = ''

    # 止盈止损
    tpTriggerPx: Optional[str] = ''
    tpOrdPx: Optional[str] = ''
    slTriggerPx: Optional[str] = ''
    slOrdPx: Optional[str] = ''
    tpTriggerPxType: Optional[str] = ''
    slTriggerPxType: Optional[str] = ''
