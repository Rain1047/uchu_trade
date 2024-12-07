from typing import Dict, List

from backend.strategy_center.ticker_price_collector import TickerPriceCollector
from backend.object_center.object_dao.algo_order_instance import AlgoOrderInstance
from backend.data_center.data_object.enum_obj import EnumOrderStatus, EnumOperationMode, EnumTdMode, EnumSide, \
    EnumAlgoOrdType, EnumTradeEnv
from backend.data_center.data_object.req.place_order.place_order_req import PostOrderReq
from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.data_api import DataAPIWrapper
from backend.decorator.decorator import *
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.utils.utils import *
from backend.constant.okx_code import *


class TradeAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        self.env = env
        self.okx = OKXAPIWrapper(env=self.env)
        self.dbApi = DataAPIWrapper()
        self.price_collector = TickerPriceCollector()
        self.session = DatabaseUtils.get_db_session()

    @add_docstring("下单")
    def post_order(self, post_req: PostOrderReq):
        # 判断order类型，当order类型为
        if post_req.ordType in ["limit", "market"]:
            print("order_instance: {}".format(post_req))
            return self.okx.trade.place_order(
                instId=post_req.instId,
                tdMode=post_req.tdMode,
                sz=post_req.sz,
                side=post_req.side,
                posSide=post_req.posSide,
                ordType=post_req.ordType,
                px=post_req.px,
                slTriggerPx=post_req.slTriggerPx,
                slOrdPx=post_req.slOrdPx
            )
        elif post_req.ordType in ["conditional", "oco", "trigger", "move_order_stop"]:
            return self.okx.trade.place_algo_order(
                instId=post_req.instId,
                tdMode=post_req.tdMode,
                sz=post_req.sz,
                side=post_req.side,
                posSide=post_req.posSide,
                ordType=post_req.ordType,
                algoClOrdId=post_req.algoClOrdId,
                slTriggerPx=post_req.slTriggerPx,
                slOrdPx=post_req.slOrdPx
            )

    @add_docstring("止损")
    def stop_loss(self, request: StopLossReq) -> Dict:
        # Step1.1 撤销自动生成止损订单
        post_order_list: list[AlgoOrderInstance] = self.session.query(AlgoOrderInstance).filter(
            AlgoOrderInstance.inst_id == request.instId,
            AlgoOrderInstance.env == self.env,
            AlgoOrderInstance.status != EnumOrderStatus.CLOSE.value
            # AlgoOrderInstance.status == '0'
        ).all()
        # Step1.2 检查是否存在自动生成的止损订单
        print(f"当前列表长度：{len(post_order_list)}")
        if len(post_order_list) > 0:
            cancel_list: List[Dict[str, str]] = []
            for post_order in post_order_list:
                print(f"当前存在的订单单号：{str(post_order.algo_id)}")
                # Step1.3 是否人工撤销

                if (self.okx.trade.get_algo_order(algoId=post_order.algo_id,
                                                  algoClOrdId=post_order.algo_cl_ord_id).get('code')
                        == ORDER_NOT_EXIST):
                    print(f"订单单号{str(post_order.algo_id)}不存在，不需要撤单")
                    post_order.operation_mode = EnumOperationMode.MANUAL.value
                    post_order.status = "close"
                else:
                    post_order.status = 'close'
                    cancel_order = FormatUtils.dao2dict(post_order, "inst_id", "algo_id")
                    print(f"Cancel Order is:{str(cancel_order)}")
                    post_order.operation_mode = EnumOperationMode.AUTO.value
                    cancel_list.append(cancel_order)
            result = self.okx.trade.cancel_algo_order(cancel_list)
            print(f"取消的结果为:{result}")
            self.session.commit()
        # 3. 获取Ticker的当前价格
        current_price = PriceUtils.get_current_ticker_price(request.instId)
        print(f"当前价格：{current_price}")

        # 4. 计算止损价格和数量
        slTriggerPx: float = 0.98
        slOrdPx: float = 0.95
        sz: float = 0.05

        # 5. POST止损订单
        result = self.okx.trade.place_algo_order(
            instId=request.instId,
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.SELL.value,
            ordType=EnumAlgoOrdType.CONDITIONAL.value,
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
            result.get('data')[0]['status'] = 'open'
            result.get('data')[0]['env'] = self.env
            self.dbApi.insert2db(result, AlgoOrderInstance)
        else:
            print(f"止损订单下单失败，原因：{result.get('msg')}")
        return result


if __name__ == '__main__':
    tradeApi_demo = TradeAPIWrapper(env=EnumTradeEnv.DEMO.value)
    print(f"当前环境：{tradeApi_demo.env}")
    print(f"当前环境：{tradeApi_demo.okx.env}")

    # 下单

    # 止损
    req = StopLossReq()
    req.instId = "ETH-USDT"
    tradeApi_demo.stop_loss(req)

    # 查询当前未结束的止损订单
    # instId = "ETH-USDT"
    # session = DatabaseUtils.get_db_session()  # 确保返回的是 Session 对象
    # query = session.query(AlgoOrderInstance).filter(
    #     AlgoOrderInstance.inst_id == instId,
    #     AlgoOrderInstance.status == '0'
    # )
    # post_order_list: list[AlgoOrderInstance] = query.all()
    # for post_order in post_order_list:
    #     print(post_order.algo_id)


