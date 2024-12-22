import okx.Trade as Trade
from typing import Optional, Dict
from backend._decorators import add_docstring, singleton
from backend.object_center.enum_obj import *


@singleton
class TradeAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag=flag, debug=False)

    @add_docstring("获取成交明细（近三天）")
    def get_fills(self, instType: Optional[str] = '', instId: Optional[str] = '', ordId: Optional[str] = ""):
        return self.tradeAPI.get_fills(
            instType=instType, instId=instId, ordId=ordId)

    @add_docstring("获取成交明细（近三个月）")
    def get_trade_fills_history(self, instType: str, **kwargs) -> Dict:
        return self.tradeAPI.get_fills_history(instType=instType, **kwargs)

    @add_docstring("获取历史订单记录（近三个月）")
    def get_orders_history_archive(self, instType: Optional[str] = 'SPOT', **kwargs) -> Dict:
        return self.tradeAPI.get_orders_history_archive(instType=instType, **kwargs)

    '''
    普通交易
    '''

    @add_docstring("获取订单信息")
    def get_order(self, instId: str, ordId: Optional[str] = "", clOrdId: Optional[str] = "") -> Dict:
        return self.tradeAPI.get_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    @add_docstring("获取未成交订单列表")
    def get_order_list(self, instType: str, instId='', ordType: Optional[str] = "", state: Optional[str] = "") -> Dict:
        return self.tradeAPI.get_order_list(instType=instType, instId=instId, ordType=ordType, state=state)

    @add_docstring("获取历史订单记录（近七天）")
    def get_orders_history(self, instType: str, instId='', ordType='', state: Optional[str] = "",
                           after='', before='', limit=''):
        return self.tradeAPI.get_orders_history(instType=instType, instId=instId, ordType=ordType, state=state,
                                                after=after, before=before, limit=limit)

    @add_docstring("下单")
    def place_order(self, instId: str, sz: str, side: Optional[str] = 'buy', posSide: Optional[str] = '',
                    tpTriggerPx: Optional[str] = '', tpOrdPx: Optional[str] = '', slTriggerPx: Optional[str] = '',
                    px: Optional[str] = '', slOrdPx: Optional[str] = "-1", tdMode: Optional[str] = 'cash',
                    ordType: Optional[str] = 'conditional', clOrdId: Optional[str] = '',
                    attachAlgoOrds: Optional[dict] = '') -> Dict:
        return self.tradeAPI.place_order(instId=instId, tdMode=tdMode, sz=sz, side=side, posSide=posSide,
                                         clOrdId=clOrdId,  # 客户自定义订单ID
                                         attachAlgoOrds=attachAlgoOrds,
                                         ordType=ordType, px=px, slTriggerPx=slTriggerPx, slOrdPx=slOrdPx)

    @add_docstring("撤销订单")
    def cancel_order(self, instId: str, ordId: Optional[str] = "", clOrdId: Optional[str] = "") -> Dict:
        return self.tradeAPI.cancel_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    @add_docstring("修改订单")
    def amend_order(self, instId: str, cxlOnFail: Optional[str] = '', ordId: Optional[str] = '',
                    clOrdId: Optional[str] = '', reqId: Optional[str] = '', newSz: Optional[str] = '',
                    newPx: Optional[str] = '', newTpTriggerPx: Optional[str] = '', newTpOrdPx: Optional[str] = '',
                    newSlTriggerPx: Optional[str] = '', newSlOrdPx: Optional[str] = '',
                    newTpTriggerPxType: Optional[str] = '', newSlTriggerPxType: Optional[str] = ''):
        return self.tradeAPI.amend_order(instId=instId, cxlOnFail=cxlOnFail, ordId=ordId, clOrdId=clOrdId, reqId=reqId,
                                         newSz=newSz, newPx=newPx, newTpTriggerPx=newTpTriggerPx, newTpOrdPx=newTpOrdPx,
                                         newSlTriggerPx=newSlTriggerPx, newSlOrdPx=newSlOrdPx,
                                         newTpTriggerPxType=newTpTriggerPxType, newSlTriggerPxType=newSlTriggerPxType)

    @add_docstring("市价仓位全平")
    def close_positions(self, instId: str, posSide: Optional[str], mgnMode: Optional[str],
                        ccy: Optional[str] = '', clOrdId: Optional[str] = '',
                        tag: Optional[str] = ''  # 订单标签
                        ):
        return self.tradeAPI.close_positions(instId=instId, posSide=posSide, mgnMode=mgnMode, ccy=ccy, clOrdId=clOrdId,
                                             tag=tag)

    '''
    策略交易
    '''

    @add_docstring("获取策略订单信息")
    def get_algo_order(self, algoId: Optional[str] = '', algoClOrdId: Optional[str] = '') -> Dict:
        return self.tradeAPI.get_algo_order_details(algoId=algoId, algoClOrdId=algoClOrdId)

    @add_docstring("获取未完成策略委托单列表")
    def order_algos_list(self, ordType: Optional[str] = EnumAlgoOrdType.CONDITIONAL.value,
                         algoId='', instType='',
                         instId='', after='',
                         before='', limit='',
                         algoClOrdId='', ):
        return self.tradeAPI.order_algos_list(ordType=ordType, algoId=algoId, instType=instType, instId=instId,
                                              after=after, before=before, limit=limit, algoClOrdId=algoClOrdId)

    @add_docstring("策略下单")
    def place_algo_order(self, instId: str, sz: str, posSide: Optional[str] = '', tpTriggerPx: Optional[str] = '',
                         tpOrdPx: Optional[str] = '', algoClOrdId: Optional[str] = '', slTriggerPx: Optional[str] = '',
                         slOrdPx: Optional[str] = '', side: Optional[str] = 'buy', tdMode: Optional[str] = 'cash',
                         ordType: Optional[str] = 'conditional') -> Dict:
        return self.tradeAPI.place_algo_order(instId=instId, tdMode=tdMode, sz=sz, side=side, posSide=posSide,
                                              ordType=ordType, algoClOrdId=algoClOrdId, slTriggerPx=slTriggerPx,
                                              slOrdPx=slOrdPx)

    @add_docstring("撤销策略订单")
    def cancel_algo_order(self, algo_orders: list) -> Dict:
        return self.tradeAPI.cancel_algo_order(algo_orders)

    @add_docstring("获取历史策略委托单列表")
    def order_algos_history(self, state: Optional[str], algoId: Optional[str] = '', instType: Optional[str] = '',
                            instId: Optional[str] = '', after: Optional[str] = '', before: Optional[str] = '',
                            limit: Optional[str] = '',
                            orderType: Optional[str] = EnumAlgoOrdType.CONDITIONAL.value):
        return self.tradeAPI.order_algos_history(state=state, algoId=algoId, instType=instType, instId=instId,
                                                 after=after, before=before, limit=limit, ordType=orderType)

    @add_docstring("修改策略委托订单")
    def amend_algo_order(self, instId='', algoId: Optional[str] = '', algoClOrdId: Optional[str] = '',
                         cxlOnFail: Optional[str] = '',
                         reqId: Optional[str] = '', newSz: Optional[str] = '', newTpTriggerPx: Optional[str] = '',
                         newTpOrdPx: Optional[str] = '', newSlTriggerPx: Optional[str] = '',
                         newSlOrdPx: Optional[str] = '',
                         newTpTriggerPxType: Optional[str] = '', newSlTriggerPxType: Optional[str] = ''):
        return self.tradeAPI.amend_algo_order(
            instId=instId, algoId=algoId, algoClOrdId=algoClOrdId, cxlOnFail=cxlOnFail, reqId=reqId, newSz=newSz,
            newTpTriggerPx=newTpTriggerPx, newTpOrdPx=newTpOrdPx, newSlTriggerPx=newSlTriggerPx, newSlOrdPx=newSlOrdPx,
            newTpTriggerPxType=newTpTriggerPxType, newSlTriggerPxType=newSlTriggerPxType)
