from typing import Optional
from pydantic import BaseModel

from backend.data_center.data_object.enum_obj import *


class PostAlgoOrderReq(BaseModel):
    """
    下单请求参数
    """
    # 基础参数
    instId: str = ''
    tdMode: EnumTdMode = EnumTdMode.CASH
    side: EnumSide = ''
    posSide: Optional[EnumPosSide] = ''
    ordType: EnumAlgoOrdType = EnumAlgoOrdType.CONDITIONAL
    sz: str = ''  # 委托数量
    algoClOrdId: Optional[str] = ''  # algo-order id

    # 计划委托 - 当ordType为trigger时有效
    triggerPx: str = ''  # 计划委托触发价
    ordPx: str = ''  # 计划委托价, -1时执行市价委托
    triggerPxType: EnumTriggerPxType = ''

    # 止盈止损 - 当ordType为conditional/oco时有效，conditional为单向，oco为双向
    # 止盈
    tpOrdPx: Optional[str] = ''
    tpTriggerPxType: Optional[EnumTriggerPxType] = ''
    tpTriggerPx: Optional[str] = ''
    tpOrdKind: Optional[EnumTpOrdKind] = ''
    # 止损
    slTriggerPx: Optional[str] = ''  # 止损触发价
    slOrdPx: Optional[str] = '-1'  # 止损委托价, -1时执行市价止损
    slTriggerPxType: Optional[EnumTriggerPxType] = ''
