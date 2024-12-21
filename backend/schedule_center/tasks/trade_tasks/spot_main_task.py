import logging
from backend.object_center._object_dao.spot_trade_config import SpotTradeConfig
from backend.schedule_center.tasks.trade_tasks.spot_sub_task_limit_order import SpotSubTaskLimitOrder

logger = logging.getLogger(__name__)


class SpotMainTask:
    def __init__(self, stop_loss_task, limit_order_task, price_service):
        self.stop_loss_task = SpotSubTaskLimitOrder()
        self.limit_order_task = SpotSubTaskLimitOrder()

    # [调度主任务] 根据配置进行止盈止损、限价委托
    async def execute_spot_main_task(self):
        # 1. 获取configs
        algo_order_configs = SpotTradeConfig().list_all()
        limit_order_configs = []
        stop_loss_configs = []
        for config in algo_order_configs:
            if config.get('type') == 'stop_loss':
                stop_loss_configs.append(config)
            elif config.get('type') == 'limit_order':
                limit_order_configs.append(config)
        # 2. 处理stop loss的任务
        if len(stop_loss_configs) > 0:
            self.stop_loss_task(stop_loss_configs)
        # 3. 处理limit order的任务
        if len(limit_order_configs) > 0:
            await self.limit_order_task.execute_limit_order_task(limit_order_configs)
