import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from pandas import DataFrame

from backend._utils import DatabaseUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.object_center._object_dao.algo_order_record import AlgoOrderRecord
from backend.object_center._object_dao.attach_algo_orders_record import AttachAlgoOrdersRecord
from backend.object_center._object_dao.st_instance import StrategyInstance
from backend.object_center.enum_obj import EnumTradeEnv, EnumState, EnumTimeFrame
from backend.service_center.okx_service.trade_swap import TradeSwapManager
from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.strategy_center.atom_strategy.strategy_utils import StrategyUtils


class StrategyModifier:
    def __init__(self, env: str = EnumTradeEnv.MARKET.value, time_frame: Optional[str] = None):
        self.env = env
        self.tf = time_frame
        self.okx_api = OKXAPIWrapper(env)
        self.trade_api = self.okx_api.trade
        self.trade_swap_manager = TradeSwapManager()
        self.data_collector = KlineDataCollector()
        self.session = DatabaseUtils.get_db_session()
        _setup_logging()

    def main_task(self):
        print("StrategyModifier@main_task, starting strategy modifier.")
        live_algo_order_record_list = AlgoOrderRecord.list_by_state(state=EnumState.LIVE.value)
        self.update_live_algo_record(live_algo_order_record_list)

        # 测试用：
        filled_algo_order_record_list = AlgoOrderRecord.list_by_state(state=EnumState.FILLED.value)
        self.update_filled_algo_record(filled_algo_order_record_list)

    def update_live_algo_record(self, live_algo_order_record_list: list):
        for algo_order_record in live_algo_order_record_list:
            print(f"StrategyModifier@main_task, processing algo order record: {algo_order_record.to_dict()}")
            get_order_result = self.trade_api.get_order(instId=algo_order_record.symbol,
                                                        ordId=algo_order_record.ord_id,
                                                        clOrdId=algo_order_record.cl_ord_id)
            print(get_order_result)
            get_order_data = get_order_result['data'][0]
            order_state = get_order_data['state']
            if order_state == EnumState.LIVE.value:
                self.handle_live_order(algo_order_record, get_order_data)
            if order_state == EnumState.FILLED.value:
                self.handle_filled_order(algo_order_record, get_order_data)

    def update_filled_algo_record(self, filled_algo_order_record_list: list):
        for algo_order_record in filled_algo_order_record_list:
            orders_history_result = self.trade_swap_manager.get_orders_history(instType="SWAP",
                                                                               instId=algo_order_record.symbol,
                                                                               before=algo_order_record.ord_id)
            # 查找特定的 attachAlgoClOrdId
            target_attach_id = algo_order_record.attach_algo_cl_ord_id
            result = self.trade_swap_manager.find_order_by_attach_algo_id(orders_history_result, target_attach_id)
            self.trade_swap_manager.save_modified_algo_order(algo_order_record, result)
            print(f"find result: {result}")

    def handle_live_order(self, algo_order_record, get_order_data):
        print("StrategyModifier@main_task, order is still live.")
        # TODO 计算新的止损价格然后设置止损，需要将原来的请求删除，并插入新的
        # 根据st_inst_id获取止损的策略code
        st_inst = StrategyInstance.get_st_instance_by_id(id=algo_order_record.st_inst_id)
        df = self.get_data_frame(st_inst)
        exit_st_code = st_inst.exit_st_code
        exit_strategy = registry.get_strategy(exit_st_code)
        exit_result = exit_strategy(df, st_inst)

        # amend_algo_order_result = self.trade_swap_manager.amend_algo_order(
        #     instId=algo_order_record.symbol,
        #     algoId=algo_order_record.attach_algo_cl_ord_id,
        #     newSz=algo_order_record.fill_sz,
        #     newPx=algo_order_record.fill_px
        # )

    def handle_filled_order(self, algo_order_record, get_order_data):
        # 1. 更新订单结果参数，调用get_order方法
        print("StrategyModifier@main_task, order is filled.")
        algo_order_record.fill_px = get_order_data['fillPx']
        algo_order_record.fill_sz = get_order_data['fillSz']
        algo_order_record.avg_px = get_order_data['avgPx']
        algo_order_record.pnl = get_order_data['pnl']
        algo_order_record.state = get_order_data['state']
        algo_order_record.lever = get_order_data['lever']
        algo_order_record.source = get_order_data['source']
        algo_order_record.update_time = datetime.now()
        AlgoOrderRecord.save_or_update_algo_order_record(algo_order_record.to_dict())
        print(get_order_data)

        attach_algo_order_result = self.trade_swap_manager.get_algo_order(
            algoId='', algoClOrdId=algo_order_record.attach_algo_cl_ord_id)
        attach_algo_orders = attach_algo_order_result['data']
        save_result = AttachAlgoOrdersRecord.save_or_update_attach_algo_orders(attach_algo_orders)

        orders_history_result = self.trade_swap_manager.get_orders_history(instType="SWAP",
                                                                           instId=algo_order_record.symbol,
                                                                           before=get_order_data['ordId'])
        print("获取历史订单记录（近七天）, 查看ordId后的记录：")
        orders_history_list = orders_history_result.get('data')
        # 查找特定的 attachAlgoClOrdId
        target_attach_id = algo_order_record.attach_algo_cl_ord_id
        result = self.trade_swap_manager.find_order_by_attach_algo_id(orders_history_result, target_attach_id)
        print(f"find result: {result}")

        print(f"StrategyModifier@update_live_algo_record save_result:{save_result}")

    def get_data_frame(self, st_instance) -> DataFrame:
        # 获取df
        symbol = st_instance.trade_pair.split('-')[0]
        interval = EnumTimeFrame.get_enum_by_value(st_instance.time_frame)
        file_abspath = self.data_collector.get_abspath(symbol=symbol, interval=interval)
        print(f"StrategyExecutor@_get_data_frame, target file path: {file_abspath}")
        df = pd.read_csv(f"{file_abspath}")
        return df


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


if __name__ == '__main__':
    strategy_modifier = StrategyModifier()
    strategy_modifier.main_task()

    # st_inst = StrategyInstance.get_st_instance_by_id(id=10)
    # df = strategy_modifier.get_data_frame(st_inst)
    # dt = pd.to_datetime("2024-12-15 11:14:22.595278")
    # index = StrategyUtils.find_kline_index_by_time(df, dt)
    # print(df.iloc[index])
