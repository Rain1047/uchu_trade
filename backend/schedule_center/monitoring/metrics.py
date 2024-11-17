# scheduler_center/monitoring/metrics.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json
import threading
from collections import defaultdict


@dataclass
class TaskMetric:
    task_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    execution_time: float = 0
    retries: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "task_name": self.task_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "success": self.success,
            "execution_time": self.execution_time,
            "retries": self.retries,
            "error_message": self.error_message
        }


class MetricsCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._metrics: Dict[str, List[TaskMetric]] = defaultdict(list)
            self._lock = threading.Lock()
            self._initialized = True

    def record_metric(self, metric: TaskMetric):
        with self._lock:
            self._metrics[metric.task_name].append(metric)

    def get_task_metrics(self, task_name: str) -> List[TaskMetric]:
        with self._lock:
            return self._metrics.get(task_name, [])

    def get_success_rate(self, task_name: str) -> float:
        metrics = self.get_task_metrics(task_name)
        if not metrics:
            return 0.0
        successful = sum(1 for m in metrics if m.success)
        return (successful / len(metrics)) * 100

    def get_average_execution_time(self, task_name: str) -> float:
        metrics = self.get_task_metrics(task_name)
        if not metrics:
            return 0.0
        times = [m.execution_time for m in metrics if m.execution_time > 0]
        return sum(times) / len(times) if times else 0.0


class MetricsReporter:
    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def generate_report(self, task_names: List[str]) -> dict:
        report = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {}
        }

        for task_name in task_names:
            metrics = self.collector.get_task_metrics(task_name)
            report["tasks"][task_name] = {
                "success_rate": self.collector.get_success_rate(task_name),
                "avg_execution_time": self.collector.get_average_execution_time(task_name),
                "total_executions": len(metrics),
                "last_execution": metrics[-1].to_dict() if metrics else None
            }

        return report

    def save_report(self, report: dict, filename: str):
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
