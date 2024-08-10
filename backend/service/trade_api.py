from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.okx_api import *


class TradeAPIWrapper:

    def __init__(self):
        self.okx = OKXAPIWrapper()

    def stop_loss(self, req: StopLossReq) -> bool:
        # 1. 获取当前Ticker

        # 2. 撤销自动生成止损订单

        # 3. 获取Ticker的当前价格

        # 4. 计算止损价格

        # 5. POST止损订单

        # 6. 成功返回True，失败返回False
        return False

