# scheduler_center/core/task_chain.py
from typing import List
import logging
from .base_task import BaseTask, TaskResult

logger = logging.getLogger(__name__)


class TaskChain:
    def __init__(self, name: str, tasks: List[BaseTask]):
        self.name = name
        self.tasks = tasks
        self.first_task = tasks[0]

        # 链接任务
        for i in range(len(tasks) - 1):
            tasks[i].set_next(tasks[i + 1])

    def execute(self) -> TaskResult:
        logger.info(f"Starting task chain '{self.name}' execution")
        try:
            result = self.first_task.execute_chain()
            if result.success:
                logger.info(f"Task chain '{self.name}' completed successfully")
            else:
                logger.error(f"Task chain '{self.name}' failed: {result.message}")
            return result
        except Exception as e:
            error_msg = f"Task chain '{self.name}' failed with unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return TaskResult(False, error_msg)
        