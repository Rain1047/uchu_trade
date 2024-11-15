
from typing import Optional, Dict, List

from backend.data_center.data_object.dao.algo_order_instance import AlgoOrderInstance
from backend.data_center.data_object.dao.fills_history import FillsHistory
from backend.data_center.data_object.req.place_order.place_order_req import PostOrderReq
from backend.data_center.data_object.req.stop_loss_req import StopLossReq
from backend.service.data_api import *
from backend.constant.okx_code import *
from backend.service.decorator import add_docstring
from backend.service.okx_api.okx_main_api import OKXAPIWrapper

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dbApi = DataAPIWrapper()
okx = OKXAPIWrapper()


@add_docstring("获取成交明细（近三个月）")
def get_fill_history(req: Optional[PageRequest] = None) -> dict:
    """
    获取成交历史记录，支持分页查询

    Args:
        req (Optional[PageRequest]): 分页请求参数，如果为None则使用默认值

    Returns:
        dict: 包含分页数据的字典，格式如下:
        {
            "items": List[FillsHistory],
            "total_count": int,
            "page_size": int,
            "page_num": int
        }
    """
    try:
        result = okx.trade.get_trade_fills_history(instType="SPOT")
        code = result['code']
        msg = result['msg']
        if code == SUCCESS_CODE:
            dbApi.insert2db(result, FillsHistory)
        else:
            print(code, msg)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")

    # 使用默认分页参数，如果请求为空
    page_request = req or PageRequest(
        pageSize=10,
        pageNum=1
    )
    # 调用数据库API获取数据
    return dbApi.page(page_request, FillsHistory)


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


# 示例用法
if __name__ == "__main__":

    okx_demo = OKXAPIWrapper(env=EnumTradeEnv.DEMO.value)
    # print(okx.apikey)
    # print(okx_demo.apikey)
    '''
    Account
    '''
    # print(okx.account.get_account_balance())
    # print(okx.account.get_positions())
    # print(okx.account.get_positions_history())
    # print(okx.account.get_account_bills_archive())
    '''
    Trade
    '''
    # print(okx.trade.get_trade_fills_history(instType="SPOT"))
    # print(okx.trade.get_orders_history_archive())
    # dbApi.insert2db(okx.trade.get_orders_history_archive(), OrderDetail)

    # 三个月的交易明细
    # res = okx.trade.get_trade_fills_history(instType="SPOT")
    # code = res['code']
    # msg = res['msg']
    # if code == SUCCESS_CODE:
    #     dbApi.insert2db(res, FillsHistory)
    #     # FillsHistory.insert_response_to_db(result, FillsHistory)
    # else:
    #     print(code, msg)
    #
    # req = PageRequest()
    # req.pageSize = 10
    # req.pageNum = 2
    # result = dbApi.page(req, FillsHistory)
    # 如果result是空，说明数据库中没有数据

    # print(result)

    # # 现货模式限价单
    # result = okx_demo.trade.place_order(
    #     instId="ETh-USDT",
    #     tdMode="cash",
    #     side="sell",
    #     ordType="limit",
    #     # px="2.15",  # 委托价格
    #     sz="0.5",  # 委托数量
    #     slTriggerPx="100",
    #     slOrdPx="90"
    # )
    # print(result)
    #
    # result = okx_demo.trade.place_algo_order(
    #     instId="ETH-USDT",
    #     tdMode="cash",
    #     side="sell",
    #     ordType="conditional",
    #     sz="0.1",
    #     tpTriggerPx="",
    #     tpOrdPx="",
    #     slTriggerPx="2400",
    #     slOrdPx="2300"
    # )
    # print(result)

    '''
    Market
    '''
    # print(okx.market.get_ticker(instId="BTC-USDT-SWAP"))
    # print(okx.market.get_candlesticks(instId="BTC-USDT", bar="1H"))

    '''
    Funding
    '''
    # print(okx.funding.get_currencies())
