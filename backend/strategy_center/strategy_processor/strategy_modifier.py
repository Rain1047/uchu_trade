import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from pandas import DataFrame

from backend._utils import DatabaseUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.object_center._object_dao.algo_order_record import AlgoOrderRecord
from backend.object_center._object_dao.st_instance import StrategyInstance
from backend.object_center.enum_obj import EnumTradeEnv, EnumState, EnumTimeFrame
from backend.service_center.okx_service.trade_swap import TradeSwapManager
from backend.strategy_center.atom_strategy.strategy_registry import registry


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
        algo_order_record_list = AlgoOrderRecord.list_by_state(state=EnumState.LIVE.value)
        for algo_order_record in algo_order_record_list:
            print("StrategyModifier@main_task, processing algo order record: {}".format(algo_order_record))
            # 通过ord_id 查询订单状态
            # 如果仍然为 live，
            get_order_result = self.trade_api.get_order(instId=algo_order_record.st_inst_id, ordId=algo_order_record.ord_id)
            order_state = get_order_result['data'][0]['state']
            if order_state == EnumState.LIVE.value:
                print("StrategyModifier@main_task, order is still live.")
                # 根据st_inst_id获取止损的策略code
                st_inst = StrategyInstance.get_st_instance_by_id(id=algo_order_record.st_inst_id)
                df = self._get_data_frame(st_inst)
                exit_st_code = st_inst.exit_st_code
                exit_strategy = registry.get_strategy(exit_st_code)
                exit_result = exit_strategy(df, st_inst)

                # amend_algo_order_result = self.trade_swap_manager.amend_algo_order(
                #     instId=algo_order_record.symbol,
                #     algoId=algo_order_record.attach_algo_cl_ord_id,
                #     newSz=algo_order_record.fill_sz,
                #     newPx=algo_order_record.fill_px
                # )

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

    def get_data_frame(self, st_instance) -> DataFrame:
        # 获取df
        symbol = st_instance.trade_pair.split('-')[0]
        interval = EnumTimeFrame.get_enum_by_value(st_instance.time_frame)
        file_abspath = self.data_collector.get_abspath(symbol=symbol, interval=interval)
        print(f"StrategyExecutor@_get_data_frame, target file path: {file_abspath}")
        df = pd.read_csv(f"{file_abspath}")
        return df

    @staticmethod
    def find_kline_index_by_time(df: pd.DataFrame, target_time):
        """
        Find the index of the corresponding kline period for a given timestamp

        Args:
            df: DataFrame with datetime index
            target_time: timestamp to look up (str or datetime)

        Returns:
            int: index of the corresponding kline period
        """
        # Convert target_time to datetime if it's string
        if isinstance(target_time, str):
            target_time = pd.to_datetime(target_time)

        # Convert datetime column to datetime type if it's not already
        if df['datetime'].dtype != 'datetime64[ns]':
            df['datetime'] = pd.to_datetime(df['datetime'])

        # Get the datetime that's less than or equal to target_time
        mask = df['datetime'] <= target_time
        if not mask.any():
            return None  # Target time is before any kline period

        return df[mask].index[-1]


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


if __name__ == '__main__':
    strategy_modifier = StrategyModifier()
    # strategy_modifier.main_task()
    st_inst = StrategyInstance.get_st_instance_by_id(id=10)
    df = strategy_modifier.get_data_frame(st_inst)
    dt = pd.to_datetime("2024-12-15 11:14:22.595278")
    index = strategy_modifier.find_kline_index_by_time(df, dt)
    print(df.iloc[index])
