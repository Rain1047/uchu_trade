import logging

from backend.data_object_center.enum_obj import EnumAutoTradeConfigType
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.schedule_center.tasks.trade_tasks.spot_limit_order_task import SpotLimitOrderTask
from backend.schedule_center.tasks.trade_tasks.spot_stop_loss_task import SpotStopLossTask
from backend.service_center.okx_service.okx_algo_order_service import OKXAlgoOrderService
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_order_service import OKXOrderService

logger = logging.getLogger(__name__)


class SpotMainTask:
    def __init__(self):
        self.okx_balance_service = OKXBalanceService()
        self.okx_order_service = OKXOrderService()
        self.okx_algo_order_service = OKXAlgoOrderService()
        self.stop_loss_task = SpotStopLossTask()
        self.limit_order_task = SpotLimitOrderTask()

    # [调度主任务] 根据配置进行止盈止损、限价委托
    def execute_spot_main_task(self):
        # 1. 检查并更新生效中的限价委托, 执行新的限价委托
        self.limit_order_task.check_and_update_auto_live_limit_order()
        self.limit_order_task.process_new_auto_limit_order_task()

        # 2. 取消所有未完成的策略委托
        self.stop_loss_task.check_and_update_auto_spot_live_algo_order()
        self.stop_loss_task.process_new_auto_stop_loss_task()


if __name__ == '__main__':
    spot_main_task = SpotMainTask()
    spot_main_task.execute_spot_main_task()
