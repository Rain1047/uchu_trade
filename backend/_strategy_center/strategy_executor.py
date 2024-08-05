import sys
import os

from backend._data_center.data_object.dao.od_instance_dao import OrderInstance
from backend._data_center.data_object.res.strategy_execute_result import StrategyExecuteResult

# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import okx.MarketData as MarketData
from backend._strategy_center.strategy_instance.entry_strategy.dbb_entry_strategy import dbb_strategy

from backend._data_center.data_object.dao.st_instance_dao import StInstance
from backend._data_center.data_object.dto.strategy_instance import StrategyInstance
import multiprocessing
from backend._service.post_order_service import *
from backend._data_center.data_object.req.post_order_req import PostOrderReq
from backend._service.utils import *
import logging
import datetime

# 创建一个字典来存储不同的策略方法
strategy_methods = {
    "dbb_strategy": dbb_strategy
}

flag = "0"  # 实盘:0 , 模拟盘：1

marketDataAPI = MarketData.MarketAPI(flag=flag)

# 获取当前时间的毫秒级别时间戳
millis_timestamp = int(time.time() * 1000)


def timestamp_to_datetime_milliseconds(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000.0
    return datetime.datetime.fromtimestamp(timestamp_sec)


dayTime = 24 * 3600 * 1000

# 创建会话实例
# session = Session()
session = DatabaseUtils.get_db_session()


# tf can be null
def main_task():
    logging.info("strategy_executor#main_task begin...")
    # 获取需要执行的规则实例，查询所有符合条件的记录
    # if tf is null how to change the query make it flexible
    instance_list = get_st_instance_list(StInstance, None)
    if instance_list:  # 检查 st_instance_list 是否为空
        # 创建进程池
        with multiprocessing.Pool() as pool:
            # 并行处理每个 st_instance
            pool.map(sub_task, instance_list)
            # 关闭进程池
            pool.close()
        sub_task(instance_list[0])


from sqlalchemy import or_


# Example function that takes a parameter tf which can be None
def get_st_instance_list(strategy, tf):
    engine = DatabaseUtils.get_db_session()
    query = engine.query(strategy).filter(
        StInstance.switch == 0,
        StInstance.is_del == 0,
        or_(StInstance.time_frame == tf, tf is None)
    )
    return query.all()


def __do2dto(st_instance):
    return StrategyInstance(
            tradePair=st_instance.trade_pair,
            timeFrame=st_instance.time_frame,
            stEntryCode=st_instance.entry_st_code,
            stExitCode=st_instance.exit_st_code,
            lossPerTrans=st_instance.loss_per_trans,
            side=st_instance.side,
        )


def post_order_request(result: StrategyExecuteResult, strategy: StrategyInstance) -> PostOrderReq:
    return PostOrderReq(
        tradeEnv=strategy.env,
        instId=strategy.tradePair,
        tdMode=EnumTdMode.ISOLATED_MARGIN.value,
        sz=str(result.sz),
        side=result.side,
        ordType=EnumOrdType.MARKET.value,
        slTriggerPx=str(result.exitPrice),
        slOrdPx="-1"
        # PostOrderReq(
        #     # 实盘&模拟
        #     tradeType=EnumTradeType.DEMO.value,
        #     instId=st_instance.trade_pair,
        #     tdMode=EnumTdMode.ISOLATED_MARGIN.value,
        #     sz=str(res.sz),
        #     side=EnumSide.BUY.value,
        #     posSide=EnumPosSide.LONG.value,
        #     ordType=EnumOrdType.MARKET.value,
        # )
        # post_order_req.slTriggerPx = str(res.exitPrice)
        # post_order_req.slOrdPx = "-1"
    )


def get_order_instance_from_result(post_order_result, order_result) -> Optional[OrderInstance]:
    data = post_order_result.get('data', [{}])[0]
    ordId = data.get('ordId', None)
    sCode = data.get('sCode', None)
    sMsg = data.get('sMsg', None)

    data_info = order_result.get('data', [{}])[0]
    accFillSz = data_info.get('accFillSz', None)
    avgPx = data_info.get('avgPx', None)
    state = data_info.get('state', None)
    posSide = data_info.get('posSide', None)
    cTime = data_info.get('cTime', None)

    if sCode == "0":
        return OrderInstance(
            order_id=ordId,
            side=EnumSide.BUY.value,
            order_info=sMsg,
            gmt_create=timestamp_to_datetime_milliseconds(int(cTime)) if cTime else None,
            gmt_modified=datetime.datetime.now(),
        )
    else:
        # Handle the error case
        return None


def sub_task(st_instance):
    logging.info(f"strategy_executor#sub_task {st_instance.trade_pair} begin...")
    try:
        st = __do2dto(st_instance)
        print(f"Sub Task Processing...")
        res = strategy_methods[st_instance.entry_st_code](st)
        print(f"Trade Pair:{st_instance.trade_pair}, Result:{res.signal}")

        if res.signal:
            post_order_req = post_order_request(res, st)
            try:
                trader = TradeAPI()
                result = trader.post_order(post_order_req)
                print(f"{datetime.datetime.now()}: {st_instance.trade_pair} trade result: {result}")
                result_info = trader.get_order_info(
                    EnumTradeType.DEMO.value,
                    st_instance.trade_pair,
                    result['data'][0]['ordId']
                )
                order_instance = get_order_instance_from_result(result, result_info)
                # 将 OrderInstance 对象添加到会话中
                if CheckUtils.is_not_empty(order_instance):
                    DatabaseUtils.save(order_instance)
                    print(f"{datetime.datetime.now()}: result_info: {result_info}")
            except Exception as e1:
                print(f"Post Order Error: {e1}")
        if not res.signal:
            print(f"{datetime.datetime.now()}: {st_instance.trade_pair} not right time to entry")
    except Exception as e2:
        print(f"{datetime.datetime.now()}: Error processing st_instance: {e2}")


if __name__ == '__main__':
    main_task()
    # st_instance_list = get_st_instance_list(StInstance, "4H")
    # for instance in st_instance_list:
    #     print(instance.id, instance.name)
