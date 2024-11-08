import okx.Account as Account
import okx.Trade as Trade
import okx.MarketData as Market
import okx.PublicData as PublicData
import okx.Funding as Funding
import okx.SpreadTrading as SpreadTrading
from typing import Optional, Dict

from backend.data_center.data_object.dao.fills_history import FillsHistory
from backend.data_center.data_object.dao.order_detail import OrderDetail
from backend.data_center.data_object.enum_obj import *
from backend.service.data_api import *
from backend.constant.okx_code import *
from backend.service.okx_api.okx_main_api import OKXAPIWrapper

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dbApi = DataAPIWrapper()
okx = OKXAPIWrapper()


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
    res = okx.trade.get_trade_fills_history(instType="SPOT")
    code = res['code']
    msg = res['msg']
    if code == SUCCESS_CODE:
        dbApi.insert2db(res, FillsHistory)
        # FillsHistory.insert_response_to_db(result, FillsHistory)
    else:
        print(code, msg)

    req = PageRequest()
    req.pageSize = 10
    req.pageNum = 2
    result = dbApi.page(req, FillsHistory)
    # 如果result是空，说明数据库中没有数据

    print(result)

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
