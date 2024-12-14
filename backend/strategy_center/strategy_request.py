from typing import Optional
from pydantic import BaseModel

from backend.object_center.enum_obj import *


class PlaceOrderRequest(BaseModel):
    """
    下单请求参数
    """
    # 基础参数
    instId: str = ''
    tdMode: EnumTdMode = ''
    side: EnumSide = ''
    ordType: EnumOrdType = ''
    sz: str = ''  # 委托数量
    clOrdId: Optional[str] = ''  # order id
    algoClOrdId: Optional[str] = ''  # algo-order id
    px: Optional[str] = ''  # 委托价格 - order
    ccy: Optional[str] = ''  # 保证金币种
    posSide: Optional[EnumPosSide] = ''  # 持仓方向
