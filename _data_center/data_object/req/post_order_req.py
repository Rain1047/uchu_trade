from typing import Optional
from pydantic import BaseModel


class PostOrderReq(BaseModel):
    # 实盘"0" 虚拟"1"
    tradeType: Optional[str] = "1"
    tradeEnv: Optional[str] = "demo"
    instId: str
    tdMode: str
    sz: str
    side: str
    # 订单类型：单向止盈止损、双向止盈止损
    ordType: str
    ccy: Optional[str] = None
    clOrdId: Optional[str] = None
    tag: Optional[str] = None
    posSide: Optional[str] = None
    reduceOnly: Optional[bool] = None
    tgtCcy: Optional[str] = None
    tpTriggerPx: Optional[str] = None
    tpOrdPx: Optional[str] = None
    slTriggerPx: Optional[str] = None
    slOrdPx: Optional[str] = None
    tpTriggerPxType: Optional[str] = None
    slTriggerPxType: Optional[str] = None
    quickMgnType: Optional[str] = None
    stpId: Optional[int] = None
    stpMode: Optional[str] = None
    px: Optional[str] = None

