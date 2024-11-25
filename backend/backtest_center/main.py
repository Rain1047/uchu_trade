import logging

from tvDatafeed import Interval

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    try:
        # 设置回测参数
        INITIAL_CASH = 100000.0
        RISK_PERCENT = 2.0
        COMMISSION = 0.001
        SYMBOL = 'BTC'
        INTERVAL = Interval.in_daily

        logger.info("开始回测流程")
        logger.info(f"参数设置: 初始资金={INITIAL_CASH}, 风险比例={RISK_PERCENT}%, 手续费率={COMMISSION}")

        # 创建回测系统
        backtest = setup_backtest(
            initial_cash=INITIAL_CASH,
            risk_percent=RISK_PERCENT,
            commission=COMMISSION
        )

        # 加载和处理数据
        logger.info(f"加载数据: {SYMBOL}, 时间间隔: {INTERVAL}")
        df = load_and_process_data(SYMBOL, INTERVAL)
        logger.info(f"数据加载完成，数据范围: {df['datetime'].min()} 到 {df['datetime'].max()}")

        # 运行回测
        logger.info("开始运行回测")
        results = backtest.run(df, plot=True)

        logger.info("回测完成")
        return results

    except Exception as e:
        logger.error(f"回测过程中发生错误: {str(e)}")
        raise


if __name__ == '__main__':
    main()
