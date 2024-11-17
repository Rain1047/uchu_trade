from backend.schedule_center.trading_scheduler import TradingScheduler


if __name__ == '__main__':
    # 创建并启动调度器
    scheduler = TradingScheduler()
    scheduler.start()
