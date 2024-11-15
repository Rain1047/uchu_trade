from functools import wraps
from typing import Optional, Dict, Type
import logging
from abc import ABC, abstractmethod

from backend.data_center.data_object.dao.order_instance import OrderInstance
from backend.data_center.data_object.dao.st_instance import StInstance
from backend.data_center.data_object.dto.strategy_instance import StrategyInstance
from backend.data_center.data_object.enum_obj import EnumTradeEnv, EnumSide, EnumTdMode, EnumOrdType, EnumTimeFrame
from backend.data_center.data_object.req.place_order.place_order_req import PostOrderReq
from backend.data_center.data_object.res.strategy_execute_result import StrategyExecuteResult
from backend.api_center.okx_api import OKXAPIWrapper
from backend.utils.utils import FormatUtils, DatabaseUtils, CheckUtils
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import dbb_strategy


class StrategyRegistry:
    """策略注册中心"""
    _strategies: Dict[str, 'TradingStrategy'] = {}

    @classmethod
    def register(cls, strategy_name: str = None):
        """
        策略注册装饰器
        @register() or @register('custom_name')
        """

        def decorator(strategy_class: Type['TradingStrategy']):
            name = strategy_name or strategy_class.__name__.lower()
            cls._strategies[name] = strategy_class()

            @wraps(strategy_class)
            def wrapper(*args, **kwargs):
                return strategy_class(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def get_strategy(cls, strategy_name: str) -> 'TradingStrategy':
        if strategy_name not in cls._strategies:
            raise ValueError(f"Strategy {strategy_name} not found")
        return cls._strategies[strategy_name]


# 基础策略接口
class TradingStrategy(ABC):
    @abstractmethod
    def execute(self, instance: 'StrategyInstance') -> 'StrategyExecuteResult':
        """执行策略并返回结果"""
        pass


# 具体策略实现
@StrategyRegistry.register('dbb_strategy')
class DBBStrategy(TradingStrategy):
    def execute(self, instance: 'StrategyInstance') -> 'StrategyExecuteResult':
        return dbb_strategy(instance)


def _handle_trade_result(trade_result: dict):
    """处理交易结果"""
    order_instance = FormatUtils.dict2dao(OrderInstance, trade_result)
    if CheckUtils.is_not_empty(order_instance):
        DatabaseUtils.save(order_instance)
        logging.info(f"Order saved successfully: {order_instance.order_id}")


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def _check_trading_signals(entry_result: Optional['StrategyExecuteResult'],
                           filter_result: Optional['StrategyExecuteResult']) -> bool:
    """
    检查交易信号是否有效

    Args:
        entry_result: 入场策略结果
        filter_result: 过滤策略结果

    Returns:
        bool: 是否应该执行交易
    """
    # 如果配置了入场策略但结果为None，不交易
    if entry_result is None or filter_result is None:
        return False

    if filter_result.signal and entry_result.signal:
        return True

    return False


class StrategyExecutor:
    def __init__(self, env: str = EnumTradeEnv.MARKET.value, time_frame: Optional[str] = None):
        self.env = env
        self.tf = time_frame
        self.okx_api = OKXAPIWrapper(env)
        self.trade_api = self.okx_api.trade_api
        _setup_logging()

    def main_task(self):
        """执行主要任务"""
        logging.info("Strategy executor starting...")
        instance_list = self._get_strategy_instances()
        for instance in instance_list:
            print("Processing strategy for {}".format(instance.trade_pair))

        if not instance_list:
            logging.info("No strategy instances found")
            return

        for instance in instance_list:
            self._process_strategy(instance)

    def _process_strategy(self, st_instance: 'StInstance'):
        """处理单个策略实例"""
        try:
            logging.info(f"Processing strategy for {st_instance.trade_pair}")
            strategy_dto = self._convert_to_dto(st_instance)
            # 使用注册中心获取并执行策略，执行入场策略
            entry_result = None
            if st_instance.entry_st_code:
                entry_strategy = StrategyRegistry.get_strategy(st_instance.entry_st_code)
                entry_result = entry_strategy.execute(strategy_dto)
                logging.info(f"Entry strategy result: {entry_result.signal if entry_result else None}")
            if entry_result is None:
                return
            # 执行过滤策略
            filter_result = None
            if st_instance.filter_st_code:
                filter_strategy = StrategyRegistry.get_strategy(st_instance.filter_st_code)
                filter_result = filter_strategy.execute(strategy_dto)
                # TODO: 过滤策略结果处理,和入场策略结果合并
                logging.info(f"Filter strategy result: {filter_result.signal if filter_result else None}")

            # 检查交易信号
            trade_signal = _check_trading_signals(entry_result, filter_result)
            if not trade_signal:
                logging.info(f"No valid trading signal for {st_instance.trade_pair}")
                return
            # 下单
            self._execute_trade(entry_result, strategy_dto)

        except Exception as e:
            logging.error(f"Error processing strategy: {e}", exc_info=True)

    def _execute_trade(self, result: 'StrategyExecuteResult', strategy: 'StrategyInstance'):
        """执行交易操作"""
        try:
            order_request = self._create_order_request(result, strategy)
            if result.side == EnumSide.BUY:
                trade_result = self.trade_api.post_order(order_request)
                _handle_trade_result(trade_result)
            elif result.side == EnumSide.SELL:
                trade_result = self.trade_api.post_order(order_request)
        except Exception as e:
            logging.error(f"Trade execution error: {e}", exc_info=True)

    def _get_strategy_instances(self) -> list:
        """获取策略实例列表"""
        session = DatabaseUtils.get_db_session()
        return session.query(StInstance).filter(
            StInstance.switch == 0,
            StInstance.is_del == 0,
            StInstance.time_frame == self.tf
        ).all()

    @staticmethod
    def _convert_to_dto(st_instance: 'StInstance') -> 'StrategyInstance':
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
            slTriggerPx=str(result.exitPrice),
            slOrdPx="-1"
        )


if __name__ == '__main__':
    executor_m4h = StrategyExecutor(env=EnumTradeEnv.MARKET.value, time_frame=EnumTimeFrame.H4_U.value)
    executor_m4h.main_task()
