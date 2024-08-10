from backend.data_center.data_object.dao.post_order import PostOrderDB
from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.okx_api import *
from backend.data_center.data_object.enum_obj import *
from backend.service.utils import *


class TradeAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        self.env = env
        self.okx = OKXAPIWrapper(env=env)

    def stop_loss(self, request: StopLossReq) -> Dict:
        # 1. 获取当前Ticker
        instId = request.instId
        # 2. 撤销自动生成止损订单

        # 3. 获取Ticker的当前价格

        # 4. 计算止损价格和数量
        slTriggerPx: float = 0.90
        slOrdPx: float = 0.95
        sz: float = 1.0

        # 5. POST止损订单
        return self.okx.trade.place_algo_order(
            instId=request.instId,
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.SELL.value,
            ordType=EnumOrdType.CONDITIONAL.value,
            clOrdId=UuidUtils.generate_32_digit_numeric_id(),
            sz=sz,
            slTriggerPx=slTriggerPx,
            slOrdPx=slOrdPx
        )


if __name__ == '__main__':
    tradeApi_demo = TradeAPIWrapper(EnumTradeEnv.DEMO.value)

    req = StopLossReq()
    req.instId = "ETH-USDT"
    dbApi.insert_order_details(tradeApi_demo.stop_loss(req), PostOrderDB)
