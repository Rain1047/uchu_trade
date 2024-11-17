# scheduler_center/monitoring/scheduler_monitor.py
from typing import Dict, List
import logging
from datetime import datetime
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.job import Job
import threading
import time


class SchedulerMonitor:
    def __init__(self, scheduler: BaseScheduler):
        self.scheduler = scheduler
        self.logger = logging.getLogger(__name__)
        self.last_run_times: Dict[str, datetime] = {}
        self.job_stats: Dict[str, Dict] = {}
        self._monitor_thread = None
        self._running = False

    def get_all_jobs(self) -> List[Dict]:
        """获取所有调度任务的状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'last_run_time': self.last_run_times.get(job.id),
                'stats': self.job_stats.get(job.id, {
                    'executions': 0,
                    'successes': 0,
                    'failures': 0
                })
            }
            jobs.append(job_info)
        return jobs

    def print_jobs_status(self):
        """打印所有任务的状态"""
        print("\n=== 调度任务状态 ===")
        print(f"当前时间: {datetime.now()}")
        print("任务列表:")
        for job in self.get_all_jobs():
            print(f"\n任务: {job['name']} (ID: {job['id']})")
            print(f"  下次执行时间: {job['next_run_time']}")
            print(f"  上次执行时间: {job['last_run_time']}")
            print(f"  执行统计:")
            print(f"    总执行次数: {job['stats']['executions']}")
            print(f"    成功次数: {job['stats']['successes']}")
            print(f"    失败次数: {job['stats']['failures']}")

    def add_listener(self):
        """添加任务执行监听器"""

        def job_executed(event):
            job_id = event.job_id
            if event.exception:
                self.logger.error(f"任务 {job_id} 执行失败: {str(event.exception)}")
                self.job_stats.setdefault(job_id, {
                    'executions': 0,
                    'successes': 0,
                    'failures': 0
                })
                self.job_stats[job_id]['executions'] += 1
                self.job_stats[job_id]['failures'] += 1
            else:
                self.logger.info(f"任务 {job_id} 执行成功")
                self.job_stats.setdefault(job_id, {
                    'executions': 0,
                    'successes': 0,
                    'failures': 0
                })
                self.job_stats[job_id]['executions'] += 1
                self.job_stats[job_id]['successes'] += 1

            self.last_run_times[job_id] = datetime.now()

        self.scheduler.add_listener(job_executed)

    def start_monitoring(self, print_interval: int = 60):
        """启动监控线程"""
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(print_interval,),
            daemon=True
        )
        self._monitor_thread.start()
        self.logger.info("调度监控已启动")

    def stop_monitoring(self):
        """停止监控线程"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.logger.info("调度监控已停止")

    def _monitor_loop(self, print_interval: int):
        """监控循环"""
        while self._running:
            self.print_jobs_status()
            time.sleep(print_interval)