import logging
from typing import Dict
from datetime import datetime
from backend.data_object_center.enum_obj import EnumTradeEnv, EnumTimeFrame
from backend.schedule_center.core.base_task import BaseTask, TaskResult, TaskConfig
from backend.strategy_center.strategy_processor.strategy_executor import StrategyExecutor
from backend._utils import DatabaseUtils


class SwapMainTask(BaseTask):

    def __init__(self, name: str, interval: str):
        """
        interval: 执行间隔，例如 "4H" 或 "15MIN"
        """
        config = TaskConfig(
            timeout=180,  # 2分钟超时
            max_retries=2,
            retry_delay=5,
            required_success=True
        )
        super().__init__(f"{name}_{interval}", config)
        self.interval = interval
        self.logger = logging.getLogger(f"strategy.{interval}")
        self.session = DatabaseUtils.get_db_session()
        self.strategy_executor_4h = StrategyExecutor(env=EnumTradeEnv.MARKET.value, time_frame=EnumTimeFrame.in_4_hour.value)
        self.strategy_executor_15min = StrategyExecutor(env=EnumTradeEnv.MARKET.value, time_frame=EnumTimeFrame.in_15_minute.value)
        self.strategy_executor_5sec = StrategyExecutor(env=EnumTradeEnv.MARKET.value, time_frame=EnumTimeFrame.in_4_hour.value)
        self.strategy_executor_map = {
            "4H": self.strategy_executor_4h,
            "15min": self.strategy_executor_15min,
            "5sec": self.strategy_executor_5sec
        }

    def execute(self) -> TaskResult:
        try:
            self.logger.info(f"PeriodicStrategyTask#execute, {self.interval} task start.")
            print(f"PeriodicStrategyTask execute {self.interval} task start.")

            # 1. 策略执行器
            executor = self.strategy_executor_map.get(self.interval)
            executor.main_task()

            # 2. 策略修改器

            return TaskResult(
                success=True,
                message=f"{self.interval} strategies executed",
                data={}
            )

        except Exception as e:
            error_msg = f"{self.interval}策略执行失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return TaskResult(False, error_msg)



