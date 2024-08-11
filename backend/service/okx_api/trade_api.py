# trade_api_wrapper.py
import okx.Trade as Trade
from typing import Optional, Dict
from backend.service.decorator import add_docstring


class TradeAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取成交明细（近三个月）")
    def get_trade_fills_history(self, instType: str, **kwargs) -> Dict:
        return self.tradeAPI.get_fills_history(instType=instType, **kwargs)

    @add_docstring("获取历史订单记录（近三个月）")
    def get_orders_history_archive(self, instType: Optional[str] = 'SPOT', **kwargs) -> Dict:
        return self.tradeAPI.get_orders_history_archive(instType=instType, **kwargs)

    @add_docstring("获取订单信息")
    def get_order(self, instId: str, ordId: Optional[str] = "", clOrdId: Optional[str] = "") -> Dict:
        return self.tradeAPI.get_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    @add_docstring("撤销订单")
    def cancel_order(self, instId: str, ordId: Optional[str] = "", clOrdId: Optional[str] = "") -> Dict:
        return self.tradeAPI.cancel_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    @add_docstring("撤销策略订单")
    def cancel_algo_order(self, algo_orders: list) -> Dict:
        return self.tradeAPI.cancel_algo_order(algo_orders)

    @add_docstring("下单")
    def place_order(self, instId: str, sz: str, side: Optional[str] = 'buy', posSide: Optional[str] = '',
                    tpTriggerPx: Optional[str] = '', tpOrdPx: Optional[str] = '', slTriggerPx: Optional[str] = '',
                    px: Optional[str] = '', slOrdPx: Optional[str] = "-1", tdMode: Optional[str] = 'cash',
                    ordType: Optional[str] = 'conditional', clOrdId: Optional[str] = '') -> Dict:
        return self.tradeAPI.place_order(instId=instId, tdMode=tdMode, sz=sz, side=side, posSide=posSide,
                                         ordType=ordType, px=px, slTriggerPx=slTriggerPx, slOrdPx=slOrdPx)

    @add_docstring("策略下单")
    def place_algo_order(self, instId: str, sz: str, posSide: Optional[str] = '', tpTriggerPx: Optional[str] = '',
                         tpOrdPx: Optional[str] = '', algoClOrdId: Optional[str] = '', slTriggerPx: Optional[str] = '',
                         slOrdPx: Optional[str] = '', side: Optional[str] = 'buy', tdMode: Optional[str] = 'cash',
                         ordType: Optional[str] = 'conditional') -> Dict:
        return self.tradeAPI.place_algo_order(instId=instId, tdMode=tdMode, sz=sz, side=side, posSide=posSide,
                                              ordType=ordType, algoClOrdId=algoClOrdId, slTriggerPx=slTriggerPx,
                                              slOrdPx=slOrdPx)
