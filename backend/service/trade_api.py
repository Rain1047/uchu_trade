from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.okx_api import *
from backend.data_center.data_object.enum_obj import *


class TradeAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        self.env = env
        self.okx = OKXAPIWrapper(env=env)

    def stop_loss(self, req: StopLossReq) -> bool:
        # 1. 获取当前Ticker

        # 2. 撤销自动生成止损订单

        # 3. 获取Ticker的当前价格

        # 4. 计算止损价格和数量
        slTriggerPx: float = 0.90
        slOrdPx: float = 0.95
        sz: float = 1.0

        # 5. POST止损订单
        result = self.okx.trade.place_algo_order(
            instId=req.instId,
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.SELL.value,
            ordType=EnumOrdType.CONDITIONAL.value,
            sz=sz,
            slTriggerPx=slTriggerPx,
            slOrdPx=slOrdPx
        )
        print(result)

        # 6. 成功返回True，失败返回False
        return False


if __name__ == '__main__':
    tradeApi_demo = TradeAPIWrapper(EnumTradeEnv.DEMO.value)

    req = StopLossReq()
    req.instId = "ETH-USDT"
    tradeApi_demo.stop_loss(req)
