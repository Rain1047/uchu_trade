from typing import Optional
from pydantic import BaseModel

from backend.data_center.data_object.enum_obj import EnumOrdType, EnumTdMode, EnumTradeEnv


class PostOrderReq(BaseModel):
    # 实盘"0" 虚拟"1"
    tradeType: Optional[str] = "1"
    tradeEnv: Optional[str] = EnumTradeEnv.DEMO.value
    instId: Optional[str] = ''
    tdMode: Optional[str] = ''
    sz: Optional[str] = ''
    side: Optional[str] = ''
    # 订单类型：单向止盈止损、双向止盈止损
    ordType: Optional[str] = ''
    ccy: Optional[str] = ''
    clOrdId: Optional[str] = ''
    tag: Optional[str] = ''
    posSide: Optional[str] = ''
    reduceOnly: Optional[bool] = ''
    tgtCcy: Optional[str] = ''
    tpTriggerPx: Optional[str] = ''
    tpOrdPx: Optional[str] = ''
    slTriggerPx: Optional[str] = ''
    slOrdPx: Optional[str] = ''
    tpTriggerPxType: Optional[str] = ''
    slTriggerPxType: Optional[str] = ''
    quickMgnType: Optional[str] = ''
    stpId: Optional[int] = ''
    stpMode: Optional[str] = ''
    px: Optional[str] = ''

    @staticmethod
    def default_post_order_req():
        return PostOrderReq(
            tradeEnv=EnumTradeEnv.DEMO.value,
            tradeType="1",
            tdMode=EnumTdMode.CASH.value,
            ordType=EnumOrdType.MARKET.value,
            slOrdPx="-1"
        )
