from typing import Optional, Dict, List

from backend.data_center.data_gather.ticker_price_collector import TickerPriceCollector
from backend.data_center.data_object.dao.post_order import PostOrderDB
from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.data_api import DataAPIWrapper
from backend.service.okx_api import *
from backend.data_center.data_object.enum_obj import *
from backend.service.okx_api.okx_main_api import OKXAPIWrapper
from backend.service.utils import *
from backend.constants import *


class TradeAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        self.env = env
        self.okx = OKXAPIWrapper(env=env)
        self.dbApi = DataAPIWrapper()
        self.price_collector = TickerPriceCollector()
        self.session = DatabaseUtils.get_db_session()

    def stop_loss(self, request: StopLossReq) -> Dict:
        # Step1.1 撤销自动生成止损订单
        post_order_list: list[PostOrderDB] = self.session.query(PostOrderDB).filter(
            PostOrderDB.inst_id == request.instId,
            # PostOrderDB.status == '0'
        ).all()
        # Step1.2 检查是否存在自动生成的止损订单
        if len(post_order_list) > 0:
            cancel_list: List[Dict[str, str]] = []
            for post_order in post_order_list:
                print(f"当前存在的订单单号：{str(post_order.algo_id)}")
                # Step1.3 是否人工撤销

                if (self.okx.trade.get_order(instId=request.instId, clOrdId=post_order.algo_id).get('code')
                        == ORDER_NOT_EXIST):
                    print(f"订单单号{str(post_order.algo_id)}不存在，不需要撤单")
                    post_order.operation_mode = EnumOperationMode.MANUAL.value
                else:
                    self.okx.trade.cancel_algo_order(instId=request.instId, clOrdId=post_order.algo_id)
                    post_order.status = '1'
                    cancel_order = FormatUtils.dao2dict(post_order, "inst_id", "algo_id")
                    print(cancel_order)
                    post_order.operation_mode = EnumOperationMode.AUTO.value

            self.okx.trade.cancel_algo_order(cancel_list)
            self.session.commit()

        # 3. 获取Ticker的当前价格
        current_price = PriceUtils.get_current_ticker_price(request.instId)

        # 4. 计算止损价格和数量
        slTriggerPx: float = 0.98
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
            self.dbApi.insert_order_details(result, PostOrderDB)
        else:
            print(f"止损订单下单失败，原因：{result.get('msg')}")
        return result


if __name__ == '__main__':
    tradeApi_demo = TradeAPIWrapper(EnumTradeEnv.DEMO.value)

    req = StopLossReq()
    req.instId = "ETH-USDT"
    tradeApi_demo.stop_loss(req)

    # 查询当前未结束的止损订单
    # instId = "ETH-USDT"
    # session = DatabaseUtils.get_db_session()  # 确保返回的是 Session 对象
    # query = session.query(PostOrderDB).filter(
    #     PostOrderDB.inst_id == instId,
    #     PostOrderDB.status == '0'
    # )
    # post_order_list: list[PostOrderDB] = query.all()
    # for post_order in post_order_list:
    #     print(post_order.algo_id)



