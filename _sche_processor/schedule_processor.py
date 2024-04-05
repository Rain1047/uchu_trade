
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from _strategy_center.strategy_executor import *
from celery_app import celery_app

def my_scheduled_job1():
    print("Job executed at:", datetime.now())


def schedule_main_task():
    main_task("4H")


# 主调度器
@celery_app.task(bind=True, name='main_processor')
def main_processor():
    # 创建调度器实例
    scheduler = BackgroundScheduler()

    # 添加作业 - 从午夜开始，每隔4小时执行一次
    # scheduler.add_job(schedule_main_task, 'cron', hour='0-23/4', minute=1, second=0)

    # 添加作业 - 从每天s的10:00开始，每隔1分钟执行一次
    scheduler.add_job(schedule_main_task, 'cron', hour=20, minute='0-59', second=0)

    # 启动调度器
    scheduler.start()

    # To keep the main thread alive
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()


if __name__ == '__main__':
    main_processor()
