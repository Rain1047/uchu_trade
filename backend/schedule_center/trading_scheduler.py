# scheduler_center/trading_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
from datetime import datetime, timedelta
from .core.task_chain import TaskChain
from backend.schedule_center.tasks.trade_tasks.data_fetch_task import TradeDataFetchTask
from backend.schedule_center.tasks.trade_tasks.period_strategy_task import PeriodicStrategyTask
from backend.schedule_center.tasks.trade_tasks.stop_loss_update_task import StopLossUpdateTask
from monitoring.alerts import AlertManager, Alert, AlertLevel, EmailAlertChannel
import logging


class TradingScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)

        # 初始化告警管理器
        self.alert_manager = AlertManager()
        # 添加邮件告警通道
        self.alert_manager.add_channel(EmailAlertChannel({
            'host': 'smtp.example.com',
            'port': 587,
            'username': 'your_email@example.com',
            'password': 'your_password',
            'from_email': 'your_email@example.com',
            'to_email': 'alerts@example.com'
        }))

    def setup_morning_tasks(self):
        """设置早上8点的任务链"""
        # 创建任务
        task_a = TradeDataFetchTask()
        task_b = StopLossUpdateTask()

        # 创建任务链
        morning_chain = TaskChain("morning_tasks", [task_a, task_b])

        # 添加到调度器
        self.scheduler.add_job(
            morning_chain.execute,
            CronTrigger(hour=8, minute=0, second=0),
            id='morning_chain',
            name='Morning Trading Tasks',
            misfire_grace_time=300  # 5分钟的容错时间
        )

    def setup_periodic_tasks(self):
        """设置周期性任务"""
        # 4小时任务
        task_4h = PeriodicStrategyTask("strategy", "4H")
        self.scheduler.add_job(
            task_4h.execute,
            CronTrigger(
                hour='8-23/4',  # 从8点开始，每4小时一次
                minute=2,
                second=0
            ),
            id='strategy_4h',
            name='4-Hour Strategy'
        )

        # 15分钟任务
        task_15min = PeriodicStrategyTask("strategy", "15MIN")
        self.scheduler.add_job(
            task_15min.execute,
            CronTrigger(
                hour='8-23',  # 8点到23点
                minute='2,17,32,47',  # 每小时的第2,17,32,47分钟
                second=0
            ),
            id='strategy_15min',
            name='15-Minute Strategy'
        )

    def start(self):
        """启动调度器"""
        try:
            # 设置所有任务
            self.setup_morning_tasks()
            self.setup_periodic_tasks()

            # 启动调度器
            self.scheduler.start()
            self.logger.info("Trading scheduler started successfully")

            # 发送启动通知
            self.alert_manager.send_alert(Alert(
                AlertLevel.INFO,
                "Trading scheduler started",
                {"start_time": datetime.now().isoformat()}
            ))

        except Exception as e:
            self.logger.error(f"Failed to start trading scheduler: {str(e)}")
            self.alert_manager.send_alert(Alert(
                AlertLevel.CRITICAL,
                "Trading scheduler failed to start",
                {"error": str(e)}
            ))
            raise

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        self.logger.info("Trading scheduler stopped")


def main():
    scheduler = TradingScheduler()
    try:
        scheduler.start()

        # 保持运行
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.stop()

    except Exception as e:
        logging.error(f"Scheduler failed: {str(e)}", exc_info=True)
        scheduler.stop()
        raise


if __name__ == '__main__':
    main()
