import logging
from abc import ABC

from backend.object_center._object_dao.spot_trade_config import SpotTradeConfig
from backend.schedule_center.tasks.trade_tasks.spot_sub_task_limit_order import SpotSubTaskLimitOrder
from backend.schedule_center.tasks.trade_tasks.spot_sub_task_stop_loss import SpotSubTaskStopLoss
from backend.service_center.okx_service.okx_algo_order_service import OKXAlgoOrderService
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService

logger = logging.getLogger(__name__)


class SpotMainTask:
    def __init__(self):
        self.okx_balance_service = OKXBalanceService()
        self.okx_algo_order_service = OKXAlgoOrderService()
        self.stop_loss_task = SpotSubTaskStopLoss()
        self.limit_order_task = SpotSubTaskLimitOrder()

    # [调度主任务] 根据配置进行止盈止损、限价委托
    async def execute_spot_main_task(self):
        # 1. 取消当前的委托
        self.okx_algo_order_service.cancel_all_spot_algo_orders()
        # 2. 获取当前生效中的现货configs
        algo_order_configs = SpotTradeConfig().list_all()
        limit_order_configs = []
        stop_loss_configs = []
        for config in algo_order_configs:
            if config.get('type') == 'stop_loss':
                stop_loss_configs.append(config)
            elif config.get('type') == 'limit_order':
                limit_order_configs.append(config)

        # 3. 处理stop loss的任务
        if len(stop_loss_configs) > 0:
            for config in stop_loss_configs:
                self.stop_loss_task.execute_stop_loss_task(config)
        # 4. 处理limit order的任务
        if len(limit_order_configs) > 0:
            for config in limit_order_configs:
                self.limit_order_task.execute_limit_order_task(config)
