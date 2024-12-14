from datetime import datetime

from backend.object_center.object_dao.algo_order_record import AlgoOrderRecord
from backend.object_center.object_dao.st_instance import StrategyInstance
from backend.object_center.enum_obj import EnumTradeEnv, EnumSide, EnumTdMode, EnumOrdType
from backend.object_center.request.place_order_req import PostOrderReq
from backend.object_center.result.strategy_execute_result import StrategyExecuteResult
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.service.okx_service.trade_swap import TradeSwapManager
from backend.utils import DatabaseUtils
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
        _setup_logging()

    def main_task(self):
        """执行主要任务"""
        print("Strategy executor start.")
        instance_list = self._get_strategy_instances()
        print("Strategy instances: {}".format(instance_list))
        if not instance_list:
            print("No strategy instances found")
            return
        for instance in instance_list:
            print("Processing strategy for {}".format(instance.trade_pair))
            self._process_strategy(instance)

    def _process_strategy(self, st_instance: 'StrategyInstance'):
        """处理单个策略实例"""
        try:
            print(f"process_strategy@processing strategy for {st_instance.trade_pair}")
            # 执行入场策略
            df = self._get_data_frame(st_instance)
            entry_result = self._execute_entry_strategy(df, st_instance)
            if not entry_result:
                print(f"process_strategy@entry result {st_instance.trade_pair} failed.")
                return

            # 执行过滤策略
            filter_result = self._execute_filter_strategy(df, st_instance)
            entry_result.signal = filter_result

            entry_result.symbol = st_instance.trade_pair
            entry_result.st_inst_id = st_instance.id
            print(f"process_strategy@entry_result {entry_result.signal} for {st_instance.trade_pair}")

            if not entry_result.signal:
                return
            # 下单
            self._execute_trade(entry_result)
        except Exception as e:
            print(f"Error processing strategy: {e}")

    @staticmethod
    def _execute_entry_strategy(df: DataFrame, st_instance: 'StrategyInstance') -> 'StrategyExecuteResult' | None:
        entry_strategy = registry.get_strategy(st_instance.entry_st_code)
        entry_result = entry_strategy(df, st_instance)
        print(f"process_strategy@entry result for {st_instance.name} is: "
              f"{entry_result.signal if entry_result else None}")
        return entry_result

    def _execute_trade(self, result: 'StrategyExecuteResult'):
        """执行交易操作"""
        try:
            trade_result = None
            if result.side == EnumSide.BUY:
                trade_result = self.trade_swap_manager.place_order(result)
            elif result.side == EnumSide.SELL:
                trade_result = self.trade_swap_manager.place_order(result)
            _handle_trade_result(result, trade_result)
        except Exception as e:
            logging.error(f"process_strategy@e_execute_trade error: {e}", exc_info=True)

    def _get_strategy_instances(self) -> list:
        """获取策略实例列表"""
        return self.session.query(StrategyInstance).filter(
            StrategyInstance.switch == 0,
            StrategyInstance.is_del == 0,
            StrategyInstance.time_frame == self.tf
        ).all()

    @staticmethod
    def _convert_to_dto(st_instance: 'StrategyInstance') -> 'StrategyInstance':
        """将DAO转换为DTO"""
        return StrategyInstance(
            tradePair=st_instance.trade_pair,
            timeFrame=st_instance.time_frame,
            stEntryCode=st_instance.entry_st_code,
            stExitCode=st_instance.exit_st_code,
            lossPerTrans=st_instance.loss_per_trans,
            side=st_instance.side,
        )

    @staticmethod
    def _create_order_request(result: 'StrategyExecuteResult',
                              strategy: 'StrategyInstance') -> 'PostOrderReq':
        """创建订单请求"""
        return PostOrderReq(
            tradeEnv=strategy.env,
            instId=strategy.trade_pair,
            tdMode=EnumTdMode.CASH if result.side == EnumSide.BUY else EnumTdMode.ISOLATED,
            sz=result.sz,
            side=result.side,
            ordType=EnumOrdType.MARKET.value,
            slTriggerPx=str(result.exit_price),
            slOrdPx="-1"
        )

    def _get_data_frame(self, st_instance) -> DataFrame:
        # 获取df
        symbol = st_instance.trade_pair.split('-')[0]
        interval = EnumTimeFrame.get_enum_by_value(st_instance.time_frame)
        file_abspath = self.data_collector.get_abspath(symbol=symbol, interval=interval)
        print(f"process_strategy@target file path: {file_abspath}")
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
                    print(f"process_strategy@filter result for {st_instance.name} is: {current_filter_result}")
            else:
                print(f"process_strategy@filter result {st_instance.trade_pair} failed.")
                return False
        else:
            return filter_result


def _handle_trade_result(st_execute_result: 'StrategyExecuteResult', trade_result: dict):
    try:
        algo_order_record = AlgoOrderRecord()

        # 从返回结果中提取第一个订单数据（data[0]）
        order_data = trade_result['data'][0]
        algo_order_record.cl_ord_id = order_data['clOrdId'],
        algo_order_record.ord_id = order_data['ordId']
        algo_order_record.s_code = order_data['sCode']
        algo_order_record.s_msg = order_data['sMsg']
        algo_order_record.ts = order_data['ts']
        algo_order_record.tag = order_data['tag']
        algo_order_record.attach_algo_cl_ord_id = trade_result['attachAlgoClOrdId']

        # 封装StrategyExecuteResult
        algo_order_record.symbol = order_data['symbol']
        algo_order_record.side = st_execute_result.side
        algo_order_record.pos_side = st_execute_result.pos_side
        algo_order_record.sz = st_execute_result.sz
        algo_order_record.st_inst_id = st_execute_result.st_inst_id
        algo_order_record.interval = st_execute_result.interval

        # 订单结果参数
        algo_order_record.pnl = '0'
        algo_order_record.lever = '5'
        algo_order_record.create_time = datetime.now()
        algo_order_record.ord_id = datetime.now()

        AlgoOrderRecord.insert(algo_order_record.to_dict())
    except Exception as e:
        print(f"process_strategy@e_handle_trade_result error: {e}")


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
