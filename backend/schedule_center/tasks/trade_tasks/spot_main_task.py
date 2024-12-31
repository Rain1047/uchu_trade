import logging

from backend.schedule_center.tasks.trade_tasks.spot_limit_order_task import SpotLimitOrderTask
from backend.schedule_center.tasks.trade_tasks.spot_order_record_task import SpotOrderRecordTask
from backend.schedule_center.tasks.trade_tasks.spot_stop_loss_task import SpotStopLossTask
logger = logging.getLogger(__name__)


class SpotMainTask:
    def __init__(self):
        self.stop_loss_task = SpotStopLossTask()
        self.limit_order_task = SpotLimitOrderTask()
        self.spot_record_task = SpotOrderRecordTask()

    # [调度主任务] 根据配置进行止盈止损、限价委托
    def execute_spot_main_task(self):
        # 1.1 检查并更新手动创建且生效中的限价委托单
        self.limit_order_task.check_and_update_manual_live_order()
        # 1.2 检查并更新自动创建且生效中的限价委托单
        self.limit_order_task.check_and_update_auto_live_order()
        # 1.3 创建新的自动限价委托单
        self.limit_order_task.process_new_auto_limit_order_task()

        # 2.1 检查并更新手动创建且生效中的自动止损单
        self.stop_loss_task.check_and_update_manual_live_algo_order()
        # 2.2 检查并更新自动创建且生效中的自动止损单
        self.stop_loss_task.check_and_update_auto_spot_live_algo_order()
        # 2.3 创建新的自动止损单
        self.stop_loss_task.process_new_auto_stop_loss_task()

        self.spot_record_task.save_update_spot_order_record()


if __name__ == '__main__':
    spot_main_task = SpotMainTask()
    spot_main_task.execute_spot_main_task()
