import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.schedule_center.monitoring.schedule_monitor import SchedulerMonitor
from backend.schedule_center.core.task_chain import TaskChain
from backend.schedule_center.tasks.trade_tasks.data_fetch_task import TradeDataFetchTask
from backend.schedule_center.tasks.trade_tasks.period_strategy_task import PeriodicStrategyTask
import logging


class TradingScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
        self.monitor = SchedulerMonitor(self.scheduler)

        # # 初始化告警管理器
        # self.alert_manager = AlertManager()
        # # 添加邮件告警通道
        # self.alert_manager.add_channel(EmailAlertChannel({
        #     'host': 'smtp.example.com',
        #     'port': 587,
        #     'username': 'your_email@example.com',
        #     'password': 'your_password',
        #     'from_email': 'your_email@example.com',
        #     'to_email': 'alerts@example.com'
        # }))

    def setup_morning_tasks(self):
        """设置早上8点的任务链"""
        # 创建任务
        data_fetch_task = TradeDataFetchTask()
        # stop_loss_task = StopLossUpdateTask()

        # 创建任务链
        morning_chain = TaskChain("morning_tasks", [data_fetch_task])

        # 添加到调度器
        self.scheduler.add_job(
            morning_chain.execute,
            CronTrigger(hour=8, minute=0, second=0),
            id='morning_chain',
            name='Morning Trading Tasks',
            misfire_grace_time=300  # 5分钟的容错时间
        )
        self.logger.info("Morning tasks scheduled successfully")

    def setup_periodic_tasks(self):
        try:
            """设置周期性任务"""
            # 4小时任务
            task_4h = PeriodicStrategyTask("strategy", "4H")
            self.scheduler.add_job(
                task_4h.execute,
                CronTrigger(
                    hour='8-23/4',  # 从8点开始，每4小时一次
                    minute=0,
                    second=10
                ),
                id='strategy_4h',
                name='4-Hour Strategy'
            )
            self.logger.info("4-hour strategy task scheduled successfully")

            # 15分钟任务
            task_15min = PeriodicStrategyTask("strategy", "15min")
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
            self.logger.info("15-minute strategy task scheduled successfully")

            task_5sec = PeriodicStrategyTask("strategy", "5sec")
            self.scheduler.add_job(
                task_5sec.execute,
                CronTrigger(
                    hour='0-23',
                    minute='0-59',
                    # second='5,10,15,20,25,30,35,40,45,50,55',
                    second='0,10,20,30,40,50'

                ),
                id='strategy_5sec',
                name='5-Sec Strategy'
            )
            self.logger.info("5-second strategy task scheduled successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup periodic tasks: {str(e)}")
            raise

    def start(self):
        """启动调度器"""
        try:
            self.logger.info("Starting trading scheduler...")
            # 设置早上八点的定时任务
            # self.setup_morning_tasks()
            # 设置周期执行的调度任务
            self.setup_periodic_tasks()

            # 启动调度器
            self.scheduler.start()
            self.logger.info("Trading scheduler started successfully.")

            # 启动监控
            self.monitor.start_monitoring(print_interval=60)  # 每30秒打印一次状态

            # 立即打印一次当前状态
            self.monitor.print_jobs_status()

            # # 发送启动通知
            # self.alert_manager.send_alert(Alert(
            #     AlertLevel.INFO,
            #     "Trading scheduler started",
            #     {"start_time": datetime.now().isoformat()}
            # ))

        except Exception as e:
            self.logger.error(f"Failed to start trading scheduler: {str(e)}")
            # self.alert_manager.send_alert(Alert(
            #     AlertLevel.CRITICAL,
            #     "Trading scheduler failed to start",
            #     {"error": str(e)}
            # ))
            raise

    def stop(self):
        """停止调度器"""
        self.monitor.stop_monitoring()
        self.scheduler.shutdown()
        self.logger.info("Trading scheduler stopped")


def main():
    # 设置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    scheduler = TradingScheduler()
    try:
        scheduler.start()

        # 保持运行
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            scheduler.stop()

    except Exception as e:
        logging.error(f"Scheduler failed: {str(e)}", exc_info=True)
        scheduler.stop()
        raise


if __name__ == '__main__':
    main()
