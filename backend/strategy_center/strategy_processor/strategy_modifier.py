import logging
from typing import Optional

from backend._utils import DatabaseUtils
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.object_center._object_dao.algo_order_record import AlgoOrderRecord
from backend.object_center.enum_obj import EnumTradeEnv, EnumState
from backend.service_center.okx_service.trade_swap import TradeSwapManager


class StrategyModifier:
    def __init__(self, env: str = EnumTradeEnv.MARKET.value, time_frame: Optional[str] = None):
        self.env = env
        self.tf = time_frame
        self.okx_api = OKXAPIWrapper(env)
        self.trade_api = self.okx_api.trade_api
        self.trade_swap_manager = TradeSwapManager()
        self.data_collector = KlineDataCollector()
        self.session = DatabaseUtils.get_db_session()
        _setup_logging()

    def main_task(self):
        print("StrategyModifier@main_task, starting strategy modifier.")
        algo_order_record_list = AlgoOrderRecord.list_by_state(state=EnumState.LIVE.value)
        for algo_order_record in algo_order_record_list:
            print("StrategyModifier@main_task, processing algo order record: {}".format(algo_order_record))


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


if __name__ == '__main__':
    strategy_modifier = StrategyModifier()
    strategy_modifier.main_task()
