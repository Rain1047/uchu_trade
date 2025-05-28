import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging
import pytz
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord
from backend.strategy_center.atom_strategy.dynamic_strategy_registry import DynamicStrategyRegistry
from backend.controller_center.backtest.enhanced_backtest_controller import run_backtest_core
from backend.schedule_center.strategy_executor import strategy_executor

logger = logging.getLogger(__name__)

class StrategyScheduler:
    """策略实例调度管理器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('America/New_York'))
        self.registry = DynamicStrategyRegistry()
        self.running_instances = {}  # 记录正在运行的实例
        
    def parse_frequency(self, frequency):
        """解析频率字符串，返回调度触发器"""
        if frequency == '1h':
            return IntervalTrigger(hours=1)
        elif frequency == '4h':
            return IntervalTrigger(hours=4)
        elif frequency == '1d':
            # 每天美东时间上午9:30运行
            return CronTrigger(hour=9, minute=30, timezone=pytz.timezone('America/New_York'))
        elif frequency == '15m':
            return IntervalTrigger(minutes=15)
        elif frequency == '5m':
            return IntervalTrigger(minutes=5)
        else:
            raise ValueError(f"不支持的频率: {frequency}")
    
    def calculate_next_execution_time(self, frequency):
        """计算下次执行时间"""
        now = datetime.now()
        if frequency == '1h':
            return now + timedelta(hours=1)
        elif frequency == '4h':
            return now + timedelta(hours=4)
        elif frequency == '1d':
            # 下一个美东时间上午9:30
            next_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time
        elif frequency == '15m':
            return now + timedelta(minutes=15)
        elif frequency == '5m':
            return now + timedelta(minutes=5)
        else:
            return now + timedelta(hours=1)
    
    def execute_strategy(self, instance_id: int):
        """执行策略（这里可以是实盘或回测）"""
        try:
            logger.info(f"开始执行策略实例 {instance_id}")
            
            # 创建执行记录
            execution_record = StrategyExecutionRecord.create(
                instance_id=instance_id,
                status='running'
            )
            
            if not execution_record:
                logger.error(f"创建执行记录失败")
                return
            
            # 执行策略（实盘模式）
            success = strategy_executor.execute_live_strategy(
                instance_id, 
                execution_record['id']
            )
            
            if success:
                # 更新执行记录状态
                StrategyExecutionRecord.update_status(
                    execution_record['id'], 
                    'completed'
                )
                
                # 更新实例统计信息
                StrategyInstance.update_execution_stats(instance_id)
                
                # 更新下次执行时间
                self._update_next_execution_time(instance_id)
                
                logger.info(f"策略实例 {instance_id} 执行完成")
            else:
                # 更新失败状态
                StrategyExecutionRecord.update_status(
                    execution_record['id'], 
                    'failed'
                )
                logger.error(f"策略实例 {instance_id} 执行失败")
                
        except Exception as e:
            logger.error(f"执行策略失败: {str(e)}")
            if 'execution_record' in locals():
                StrategyExecutionRecord.update_status(
                    execution_record['id'], 
                    'failed'
                )
    
    def _update_next_execution_time(self, instance_id: int):
        """更新下次执行时间"""
        try:
            instance = StrategyInstance.get_by_id(instance_id)
            if instance:
                next_time = self.calculate_next_execution_time(instance['schedule_frequency'])
                StrategyInstance.update_execution_time(
                    instance_id, 
                    datetime.now(), 
                    next_time
                )
        except Exception as e:
            logger.error(f"更新下次执行时间失败: {str(e)}")
    
    def add_instance_job(self, instance_id):
        """添加策略实例的调度任务"""
        try:
            instance = StrategyInstance.get_by_id(instance_id)
            if not instance:
                logger.error(f"策略实例 {instance_id} 不存在")
                return False
            
            # 获取调度触发器
            trigger = self.parse_frequency(instance['schedule_frequency'])
            
            # 添加任务
            job_id = f"strategy_instance_{instance_id}"
            self.scheduler.add_job(
                self.execute_strategy,
                trigger,
                args=[instance_id],
                id=job_id,
                name=f"{instance['strategy_name']} - {instance['schedule_frequency']}",
                misfire_grace_time=300  # 5分钟容错
            )
            
            # 记录运行中的实例
            self.running_instances[instance_id] = job_id
            
            # 更新状态和下次执行时间
            StrategyInstance.update_status(instance_id, 'running')
            next_time = self.calculate_next_execution_time(instance['schedule_frequency'])
            StrategyInstance.update_execution_time(instance_id, None, next_time)
            
            logger.info(f"策略实例 {instance_id} 已添加到调度器")
            return True
            
        except Exception as e:
            logger.error(f"添加策略实例 {instance_id} 到调度器失败: {str(e)}")
            return False
    
    def remove_instance_job(self, instance_id):
        """移除策略实例的调度任务"""
        try:
            job_id = self.running_instances.get(instance_id)
            if job_id:
                self.scheduler.remove_job(job_id)
                del self.running_instances[instance_id]
                StrategyInstance.update_status(instance_id, 'stopped')
                logger.info(f"策略实例 {instance_id} 已从调度器移除")
                return True
            return False
        except Exception as e:
            logger.error(f"移除策略实例 {instance_id} 失败: {str(e)}")
            return False
    
    def pause_instance_job(self, instance_id):
        """暂停策略实例"""
        try:
            job_id = self.running_instances.get(instance_id)
            if job_id:
                self.scheduler.pause_job(job_id)
                StrategyInstance.update_status(instance_id, 'paused')
                logger.info(f"策略实例 {instance_id} 已暂停")
                return True
            return False
        except Exception as e:
            logger.error(f"暂停策略实例 {instance_id} 失败: {str(e)}")
            return False
    
    def resume_instance_job(self, instance_id):
        """恢复策略实例"""
        try:
            job_id = self.running_instances.get(instance_id)
            if job_id:
                self.scheduler.resume_job(job_id)
                StrategyInstance.update_status(instance_id, 'running')
                logger.info(f"策略实例 {instance_id} 已恢复")
                return True
            return False
        except Exception as e:
            logger.error(f"恢复策略实例 {instance_id} 失败: {str(e)}")
            return False
    
    def start(self):
        """启动调度器"""
        self.scheduler.start()
        logger.info("策略调度器已启动")
        
        # 恢复之前运行的实例
        running_instances = StrategyInstance.list_all(status='running')
        for instance in running_instances:
            self.add_instance_job(instance['id'])
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("策略调度器已停止")
    
    def get_scheduler_status(self):
        """获取调度器状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None,
                'state': 'running' if job.next_run_time else 'paused'
            })
        return {
            'running': self.scheduler.running,
            'jobs': jobs,
            'total_jobs': len(jobs)
        }

# 全局调度器实例
strategy_scheduler = StrategyScheduler() 