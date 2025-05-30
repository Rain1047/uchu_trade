from backend.data_object_center.st_instance import StrategyInstance
from backend.data_object_center.enum_obj import EnumTradeEnv
from backend.service_center.okx_service.okx_algo_order_service import OKXAlgoOrderService
from backend.strategy_center.strategy_result import StrategyExecuteResult
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend._utils import DatabaseUtils, SymbolFormatUtils
from backend.service_center.okx_service.trade_swap import TradeSwapManager
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import registry
from backend.data_center.kline_data.kline_data_collector import *
import pandas as pd


class StrategyExecutor:
    def __init__(self, env: str = EnumTradeEnv.MARKET.value, time_frame: Optional[str] = None):
        self.env = env
        self.tf = time_frame
        self.okx_api = OKXAPIWrapper(env)
        self.trade_api = self.okx_api.trade_api
        self.trade_swap_manager = TradeSwapManager()
        self.data_collector = KlineDataCollector()
        self.session = DatabaseUtils.get_db_session()
        self.okx_algo_order_service = OKXAlgoOrderService()
        _setup_logging()

    def main_task(self):
        """根据策略配置判断是否下单并且执行"""
        print(f"StrategyExecutor@main_task, algo order executor start.")
        instance_list = self._get_strategy_instances()
        print("StrategyExecutor@strategy instances: {}".format(instance_list))
        if not instance_list:
            print("StrategyExecutor@main_task, no strategy instances found.")
            return
        for instance in instance_list:
            print("StrategyExecutor@main_task, processing strategy for {}".format(instance.trade_pair))
            self._process_strategy(instance)

    def _process_strategy(self, st_instance: 'StrategyInstance'):
        """处理单个策略实例"""
        try:
            print(f"StrategyExecutor@_process_strategy, processing strategy for {st_instance.trade_pair}")
            # 1.入场策略
            df = self._get_data_frame(st_instance)
            entry_result = self._execute_entry_strategy(df, st_instance)
            if not entry_result:
                print(f"StrategyExecutor@_process_strategy entry result {st_instance.trade_pair} failed.")
                return

            # 2.过滤策略
            filter_result = self._execute_filter_strategy(df, st_instance)
            entry_result.signal = filter_result

            entry_result.symbol = st_instance.trade_pair
            entry_result.st_inst_id = st_instance.id
            print(f"StrategyExecutor@_process_strategy, filter result is {entry_result.signal} for {st_instance.trade_pair}")

            if not entry_result.signal:
                return
            # 3.下单
            trade_result = self.okx_algo_order_service.place_order_by_st_result(entry_result)
            # 4.保存交易记录
            self.okx_algo_order_service.save_execute_algo_order_result(
                st_execute_result=entry_result, place_order_result=trade_result)

        except Exception as e:
            print(f"StrategyExecutor@_process_strategy Error processing strategy: {e}")

    @staticmethod
    def _execute_entry_strategy(df: DataFrame, st_instance: 'StrategyInstance') -> 'StrategyExecuteResult' | None:
        entry_strategy = registry.get_strategy(st_instance.entry_st_code)
        entry_result = entry_strategy(df, st_instance)
        print(f"StrategyExecutor@_execute_entry_strategy result for {st_instance.name} is: "
              f"{entry_result.signal if entry_result else None}")
        return entry_result

    def _execute_trade(self, st_result: 'StrategyExecuteResult'):
        """执行交易操作"""
        try:
            trade_result = self.okx_algo_order_service.place_order_by_st_result(st_result)
            self.okx_algo_order_service.save_execute_algo_order_result(st_result, trade_result)
            return trade_result
        except Exception as e:
            logging.error(f"StrategyExecutor@_execute_trade, error: {e}", exc_info=True)

    def _get_strategy_instances(self) -> list:
        """获取策略实例列表"""
        return self.session.query(StrategyInstance).filter(
            StrategyInstance.switch == 0,
            StrategyInstance.is_del == 0,
            StrategyInstance.time_frame == self.tf
        ).all()

    def _get_data_frame(self, st_instance) -> DataFrame:
        # 获取df
        symbol = st_instance.trade_pair.split('-')[0]
        interval = EnumTimeFrame.get_enum_by_value(st_instance.time_frame)
        file_abspath = self.data_collector.get_abspath(symbol=symbol, interval=interval)
        print(f"StrategyExecutor@_get_data_frame, target file path: {file_abspath}")
        df = pd.read_csv(f"{file_abspath}")
        return df

    @staticmethod
    def _execute_filter_strategy(df: pd.DataFrame, st_instance: 'StrategyInstance'):
        filter_result = True
        if st_instance.filter_st_code:
            filter_strategy_list = st_instance.filter_st_code.split(',')
            if len(filter_strategy_list) > 1:
                for filter_strategy_code in filter_strategy_list:
                    filter_strategy = registry.get_strategy(filter_strategy_code)
                    current_filter_result = filter_strategy(df, st_instance)
                    # 如果任何一个过滤策略返回False，将filter_result设为False
                    if not current_filter_result:
                        filter_result = False
                        break
            else:
                filter_result = False
            print(f"StrategyExecutor@_execute_filter_strategy , "
                  f"filter result for {st_instance.name} is: {filter_result}")
            return filter_result
        else:
            return filter_result


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def _check_trading_signals(entry_result: Optional['StrategyExecuteResult']) -> bool:
    if entry_result is None:
        return False

    if entry_result.signal:
        return True

    return False


if __name__ == '__main__':
    st_result = StrategyExecuteResult()
    okx_algo_order_service = OKXAlgoOrderService()
    st_result.symbol = "ETH-USDT"
    format_symbol = SymbolFormatUtils.get_swap_usdt(st_result.symbol)
    st_result.symbol = format_symbol
    st_result.side = "buy"
    st_result.pos_side = "long"
    st_result.sz = "1"
    st_result.st_inst_id = 1
    st_result.stop_loss_price = "3300"
    st_result.signal = True
    trade_result = okx_algo_order_service.place_order_by_st_result(st_result)
    save_result = okx_algo_order_service.save_execute_algo_order_result(st_result, trade_result)



