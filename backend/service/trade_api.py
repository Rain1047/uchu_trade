from backend.data_center.data_gather.ticker_price_collector import TickerPriceCollector
from backend.data_center.data_object.dao.post_order import PostOrderDB
from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.okx_api import *
from backend.data_center.data_object.enum_obj import *
from backend.service.utils import *


class TradeAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        self.env = env
        self.okx = OKXAPIWrapper(env=env)
        self.price_collector = TickerPriceCollector()

    def stop_loss(self, request: StopLossReq) -> Dict:
        # 1. 获取当前Ticker
        instId = request.instId
        # 2. 撤销自动生成止损订单


        # 3. 获取Ticker的当前价格
        current_price = PriceUtils.get_current_ticker_price(instId)

        # 4. 计算止损价格和数量
        slTriggerPx: float = 0.90
        slOrdPx: float = 0.95
        sz: float = 0.05

        # 5. POST止损订单
        result = self.okx.trade.place_algo_order(
            instId=request.instId,
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.SELL.value,
            ordType=EnumOrdType.CONDITIONAL.value,
            algoClOrdId=UuidUtils.generate_32_digit_numeric_id(),
            sz=sz,
            slTriggerPx=slTriggerPx,
            slOrdPx=slOrdPx
        )
        if result.get('code') == '0':
            print(f"止损订单下单成功，订单号：{result.get('data')[0].get('algoClOrdId')}")
            result.get('data')[0]['instId'] = request.instId
            result.get('data')[0]['side'] = EnumSide.SELL.value
            result.get('data')[0]['c_time'] = str(DateUtils.milliseconds())
            result.get('data')[0]['u_time'] = str(DateUtils.milliseconds())
            result.get('data')[0]['status'] = '0'
            dbApi.insert_order_details(result, PostOrderDB)
        else:
            print(f"止损订单下单失败，原因：{result.get('msg')}")
        return result


if __name__ == '__main__':
    tradeApi_demo = TradeAPIWrapper(EnumTradeEnv.DEMO.value)

    req = StopLossReq()
    req.instId = "ETH-USDT"
    tradeApi_demo.stop_loss(req)
