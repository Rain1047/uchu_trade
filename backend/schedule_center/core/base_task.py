# scheduler_center/core/base_task.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
import logging
from functools import wraps
from datetime import datetime
import threading
from contextlib import contextmanager


class TaskTimeoutError(Exception):
    pass


class TaskResult:
    def __init__(self, success: bool, message: str, data: Optional[dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.execution_time: float = 0
        self.retries: int = 0
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "execution_time": self.execution_time,
            "retries": self.retries,
            "timestamp": self.timestamp.isoformat()
        }


class TaskConfig:
    def __init__(self,
                 timeout: int = 60,  # 默认超时时间60秒
                 max_retries: int = 3,  # 默认最大重试次数
                 retry_delay: int = 5,  # 默认重试延迟5秒
                 required_success: bool = True  # 是否要求任务成功才继续
                 ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.required_success = required_success


@contextmanager
def timeout_context(seconds: int):
    """超时控制上下文管理器"""
    timer = threading.Timer(seconds, lambda: (_ for _ in ()).throw(TaskTimeoutError))
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


class BaseTask(ABC):
    def __init__(self, name: str, config: Optional[TaskConfig] = None):
        self.name = name
        self.next_task: Optional[BaseTask] = None
        self.config = config or TaskConfig()
        self.logger = logging.getLogger(f"task.{name}")

    def set_next(self, task: 'BaseTask') -> 'BaseTask':
        self.next_task = task
        return task

    def with_retry(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> TaskResult:
            last_exception = None
            result = TaskResult(False, "Task not executed")

            for attempt in range(self.config.max_retries + 1):
                try:
                    if attempt > 0:
                        self.logger.info(f"Retrying {self.name} (attempt {attempt + 1}/{self.config.max_retries + 1})")
                        time.sleep(self.config.retry_delay)

                    with timeout_context(self.config.timeout):
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        result.execution_time = time.time() - start_time
                        result.retries = attempt

                        if result.success:
                            return result

                except TaskTimeoutError:
                    last_exception = f"Task {self.name} timed out after {self.config.timeout} seconds"
                    self.logger.error(last_exception)
                except Exception as e:
                    last_exception = str(e)
                    self.logger.error(f"Task {self.name} failed: {str(e)}", exc_info=True)

                if attempt < self.config.max_retries:
                    continue

                result.message = f"Task failed after {attempt + 1} attempts. Last error: {last_exception}"
                return result

            return result

    def execute_chain(self) -> TaskResult:
        self.logger.info(f"Starting execution of task: {self.name}")

        result = self.with_retry(self.execute)()
        self.logger.info(f"Task {self.name} completed with result: {result.to_dict()}")

        if not result.success and self.config.required_success:
            self.logger.error(f"Chain execution stopped at {self.name} due to failure")
            return result

        if self.next_task:
            self.logger.info(f"Proceeding to next task: {self.next_task.name}")
            next_result = self.next_task.execute_chain()
            next_result.data.update({"previous_task": result.to_dict()})
            return next_result

        return result

    @abstractmethod
    def execute(self) -> TaskResult:
        pass