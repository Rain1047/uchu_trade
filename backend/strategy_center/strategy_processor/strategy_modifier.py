import logging
from datetime import datetime
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
            # 1. 通过ord_id 查询订单状态
            # 如果仍然为 live，
            get_order_result = self.trade_api.get_order(instId=algo_order_record.symbol, ordId=algo_order_record.ord_id)
            order_state = get_order_result['data'][0]['state']
            if order_state == EnumState.LIVE.value:
                print("StrategyModifier@main_task, order is still live, do nothing.")
            if order_state == EnumState.FILLED.value:
                print("StrategyModifier@main_task, order is filled.")
                # 订单结果参数，调用get_order方法
                get_order_result = self.trade_swap_manager.get_order(
                    instId=algo_order_record.symbol,
                    ordId=algo_order_record.ord_id,
                    clOrdId=algo_order_record.cl_ord_id
                )
                get_order_data = get_order_result['data'][0]
                algo_order_record.fill_px = get_order_data['fillPx']
                algo_order_record.fill_sz = get_order_data['fillSz']
                algo_order_record.avg_px = get_order_data['avgPx']
                algo_order_record.pnl = get_order_data['pnl']
                algo_order_record.state = get_order_data['state']
                algo_order_record.lever = get_order_data['lever']
                algo_order_record.update_time = datetime.now()
                AlgoOrderRecord.save_or_update_algo_order_record(algo_order_record.to_dict())
                print(get_order_data)


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


if __name__ == '__main__':
    strategy_modifier = StrategyModifier()
    strategy_modifier.main_task()
