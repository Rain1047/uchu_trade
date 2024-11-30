import sys
from abc import abstractmethod, ABC
from typing import Dict
from sqlalchemy import or_

from backend.data_center.data_object.enum_obj import EnumTradeEnv, EnumSide, EnumTdMode, EnumOrdType
from backend.service.trade_api import TradeAPIWrapper
from backend.utils.utils import *
from backend.object_center.object_dao.order_instance import OrderInstance
from backend.data_center.data_object.res.strategy_execute_result import StrategyExecuteResult
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper

# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import dbb_entry_long_strategy_live
from backend.object_center.object_dao.st_instance import StInstance
from backend.data_center.data_object.dto.strategy_instance import StrategyInstance
from backend.data_center.data_object.req.place_order.place_order_req import PostOrderReq
from backend.utils.utils import *
import logging
import datetime

# 创建一个字典来存储不同的策略方法
strategy_methods = {
    "dbb_strategy": dbb_entry_long_strategy_live
}

# 获取当前时间的毫秒级别时间戳
millis_timestamp = int(time.time() * 1000)


def timestamp_to_datetime_milliseconds(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000.0
    return datetime.datetime.fromtimestamp(timestamp_sec)


dayTime = 24 * 3600 * 1000

# 创建会话实例
# session = Session()
session = DatabaseUtils.get_db_session()


# 基础策略接口
class TradingStrategy(ABC):
    @abstractmethod
    def execute(self, instance: 'StrategyInstance') -> 'StrategyExecuteResult':
        """执行策略并返回结果"""
        pass


# 具体策略实现
class DBBStrategy(TradingStrategy):
    def execute(self, instance: 'StrategyInstance') -> 'StrategyExecuteResult':

        return dbb_entry_long_strategy_live(instance)


# 简单的策略工厂
class StrategyFactory:
    _strategies: Dict[str, TradingStrategy] = {
        "dbb_strategy": DBBStrategy()
    }

    @classmethod
    def get_strategy(cls, strategy_name: str) -> TradingStrategy:
        strategy = cls._strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"Strategy {strategy_name} not found")
        return strategy

    @classmethod
    def register_strategy(cls, name: str, strategy: TradingStrategy):
        cls._strategies[name] = strategy


class StrategyExecutor:
    def __init__(self, env: Optional[str] = EnumTradeEnv.DEMO.value, time_frame: Optional[str] = None):
        self.env = env
        self.tf = time_frame
        self.instance_list = self.get_st_instance_list(StInstance, self.tf)

    def main_task(self):
        logging.info("strategy_executor#main_task begin...")
        # 获取需要执行的规则实例，查询所有符合条件的记录
        if self.instance_list:
            print(f"Instance List: {self.instance_list}")

            # with ProcessPoolExecutor() as executor:
            #     # 使用 lambda 传递额外的参数
            #     futures = [executor.submit(self.sub_task, instance, self.env)
            #                for instance in self.instance_list]
            #     # 等待所有 futures 完成
            #     for future in futures:
            #         future.result()

    def sub_task(self, st_instance, env: str):
        okx = OKXAPIWrapper(env)
        trade_api = TradeAPIWrapper(env)
        logging.info(f"strategy_executor#sub_task {st_instance.trade_pair} begin...")
        try:
            st = self.__do2dto(st_instance)
            print(f"Sub Task Processing...")
            # 1. 执行策略，获取结果
            res = strategy_methods[st_instance.entry_st_code](st)
            print(f"Trade Pair:{st_instance.trade_pair}, Result:{res.signal}")

            # 2. 当交易信号为True时
            if res.signal:
                post_order_req = get_post_order_request(res, st)
                # 2.1 方向为BUY
                if res.side == EnumSide.BUY:
                    try:
                        result = trade_api.post_order(post_order_req)
                        print(f"{datetime.datetime.now()}: {st_instance.trade_pair} "
                              f"trade result: {result}")
                        order_instance = FormatUtils.dict2dao(OrderInstance, result)
                        if CheckUtils.is_not_empty(order_instance):
                            DatabaseUtils.save(order_instance)
                    except Exception as e1:
                        print(f"Post Order Error: {e1}")
                # 2.2 方向为SELL
                if res.side == EnumSide.SELL:
                    pass
            # 无交易信号时，跳过
            if not res.signal:
                print(f"{datetime.datetime.now()}: "
                      f"{st_instance.trade_pair} not right time to entry")
        except Exception as e2:
            print(f"{datetime.datetime.now()}: Error processing st_instance: {e2}")

    @staticmethod
    def get_st_instance_list(strategy, tf) -> list[StInstance]:
        engine = DatabaseUtils.get_db_session()
        query = engine.query(strategy).filter(
            StInstance.switch == 0,
            StInstance.is_del == 0,
            or_(StInstance.time_frame == tf, tf is None)
        )
        return query.all()

    @staticmethod
    def __do2dto(st_instance):
        return StrategyInstance(
            tradePair=st_instance.trade_pair,
            timeFrame=st_instance.time_frame,
            stEntryCode=st_instance.entry_st_code,
            stExitCode=st_instance.exit_st_code,
            lossPerTrans=st_instance.loss_per_trans,
            side=st_instance.side,
        )


def get_post_order_request(result: StrategyExecuteResult, strategy: StrategyInstance) -> PostOrderReq:
    return PostOrderReq(
        tradeEnv=strategy.env,
        instId=strategy.trade_pair,
        tdMode=EnumTdMode.CASH if result.side == EnumSide.BUY else EnumTdMode.ISOLATED,
        sz=result.sz,
        side=result.side,
        ordType=EnumOrdType.MARKET.value,
        slTriggerPx=str(result.exitPrice),
        slOrdPx="-1"
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


if __name__ == '__main__':
    se = StrategyExecutor(env=EnumTradeEnv.DEMO.value)
    se.main_task()
    # st_instance_list = get_st_instance_list(StInstance, "4H")
    # for instance in st_instance_list:
    #     print(instance.id, instance.name)
