import logging

from backend.data_object_center.enum_obj import EnumAutoTradeConfigType
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.schedule_center.tasks.trade_tasks.spot_sub_task_limit_order import SpotSubTaskLimitOrder
from backend.schedule_center.tasks.trade_tasks.spot_sub_task_stop_loss import SpotSubTaskStopLoss
from backend.service_center.okx_service.okx_algo_order_service import OKXAlgoOrderService
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_order_service import OKXOrderService

logger = logging.getLogger(__name__)


class SpotMainTask:
    def __init__(self):
        self.okx_balance_service = OKXBalanceService()
        self.okx_order_service = OKXOrderService()
        self.okx_algo_order_service = OKXAlgoOrderService()
        self.stop_loss_task = SpotSubTaskStopLoss()
        self.limit_order_task = SpotSubTaskLimitOrder()

    # [调度主任务] 根据配置进行止盈止损、限价委托
    def execute_spot_main_task(self):
        # 1. 检查并更新生效中的限价委托
        self.limit_order_task.check_and_update_auto_spot_live_order()

        # 2. 取消所有未完成的策略委托
        self.stop_loss_task.check_and_update_auto_spot_live_algo_order()

        # 3. 获取当前生效中的现货configs
        algo_order_configs = SpotTradeConfig().list_all()
        limit_order_configs = []
        stop_loss_configs = []
        for config in algo_order_configs:
            exec_nums = config.get('exec_nums')
            if exec_nums <= 0:
                print(f"Exec config: {config.get('id')} task finished.")
                continue
            if config.get('type') == EnumAutoTradeConfigType.STOP_LOSS.value:
                stop_loss_configs.append(config)
            elif config.get('type') == EnumAutoTradeConfigType.LIMIT_ORDER.value:
                limit_order_configs.append(config)
        # 3. 处理stop loss的任务
        print(stop_loss_configs)
        if len(stop_loss_configs) > 0:
            for config in stop_loss_configs:
                print(config)
                self.stop_loss_task.execute_stop_loss_task(config)
        # 4. 处理limit order的任务
        if len(limit_order_configs) > 0:
            for config in limit_order_configs:
                print(config)
                self.limit_order_task.execute_limit_order_task(config)


if __name__ == '__main__':
    spot_main_task = SpotMainTask()
    spot_main_task.execute_spot_main_task()
