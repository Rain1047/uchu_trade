# scheduler_center/tasks/common_tasks.py
from typing import Optional
from ..core.base_task import BaseTask, TaskResult, TaskConfig


class DataFetchTask(BaseTask):
    def __init__(self, name: str, config: Optional[TaskConfig] = None):
        super().__init__(name, config or TaskConfig(
            timeout=30,  # 数据获取超时30秒
            max_retries=3,
            retry_delay=5
        ))

    def execute(self) -> TaskResult:
        try:
            # 实现数据获取逻辑
            self.logger.info("Fetching data...")
            # TODO: 实现具体的数据获取逻辑
            return TaskResult(True, "Data fetched successfully", {"data": "example_data"})
        except Exception as e:
            self.logger.error(f"Data fetch failed: {str(e)}", exc_info=True)
            return TaskResult(False, f"Data fetch failed: {str(e)}")


class AnalysisTask(BaseTask):
    def __init__(self, name: str, config: Optional[TaskConfig] = None):
        super().__init__(name, config or TaskConfig(
            timeout=60,  # 分析任务超时60秒
            max_retries=2,
            retry_delay=10
        ))

    def execute(self) -> TaskResult:
        try:
            self.logger.info("Analyzing data...")
            # TODO: 实现具体的分析逻辑
            return TaskResult(True, "Analysis completed successfully")
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return TaskResult(False, f"Analysis failed: {str(e)}")


class ExecutionTask(BaseTask):
    def __init__(self, name: str, config: Optional[TaskConfig] = None):
        super().__init__(name, config or TaskConfig(
            timeout=30,
            max_retries=1,  # 执行任务只重试一次
            retry_delay=5,
            required_success=True
        ))

    def execute(self) -> TaskResult:
        try:
            self.logger.info("Executing trade...")
            # TODO: 实现具体的交易执行逻辑
            return TaskResult(True, "Execution completed successfully")
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}", exc_info=True)
            return TaskResult(False, f"Execution failed: {str(e)}")
