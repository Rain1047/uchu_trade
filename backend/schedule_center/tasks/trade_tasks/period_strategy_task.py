import logging
from typing import Dict, Any, List
from datetime import datetime
from backend.data_center.data_object.enum_obj import EnumTradeEnv, EnumTimeFrame
from backend.schedule_center.core.base_task import BaseTask, TaskResult, TaskConfig
from backend.strategy_center.strategy_processor.strategy_executor import StrategyExecutor
from backend.utils.utils import DatabaseUtils


class StrategyExecutionResult:
    def __init__(self, strategy_id: int, success: bool, message: str, data: Dict = None):
        self.strategy_id = strategy_id
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'strategy_id': self.strategy_id,
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class PeriodicStrategyTask(BaseTask):
    """周期性策略执行任务"""

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
        self.strategy_executor_4h = StrategyExecutor(env=EnumTradeEnv.MARKET.value, time_frame=EnumTimeFrame.H4_U.value)

    def execute(self) -> TaskResult:
        try:
            self.logger.info(f"PeriodicStrategyTask#execute, {self.interval} task start.")
            print(f"PeriodicStrategyTask execute {self.interval} task start.")

            # 2. 执行策略
            self.strategy_executor_4h.main_task()

            return TaskResult(
                success=True,
                message=f"{self.interval} strategies executed",
                data= True
            )

        except Exception as e:
            error_msg = f"{self.interval}策略执行失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return TaskResult(False, error_msg)



