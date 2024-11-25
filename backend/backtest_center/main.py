import logging
import pandas as pd
from pathlib import Path
from tvDatafeed import Interval

from core.backtest_system import BacktestSystem
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import dbb_entry_long_strategy_backtest
from backend.strategy_center.atom_strategy.exit_strategy.dbb_exist_strategy import dbb_exist_strategy_for_backtest

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_backtest(
        initial_cash: float = 100000.0,
        risk_percent: float = 2.0,
        commission: float = 0.001
) -> BacktestSystem:
    """
    设置回测系统

    Args:
        initial_cash: 初始资金
        risk_percent: 风险百分比
        commission: 手续费率

    Returns:
        BacktestSystem: 配置好的回测系统实例
    """
    return BacktestSystem(
        initial_cash=initial_cash,
        risk_percent=risk_percent,
        commission=commission
    )


def load_and_process_data(symbol: str, interval: Interval) -> pd.DataFrame:
    """
    加载和处理数据

    Args:
        symbol: 交易对符号
        interval: 时间间隔

    Returns:
        pd.DataFrame: 处理后的数据

    Raises:
        FileNotFoundError: 数据文件不存在
        ValueError: 数据处理过程中的错误
    """
    try:
        # 获取数据
        tv = KlineDataCollector()
        file_abspath = tv.get_abspath(symbol=symbol, interval=interval)

        if not Path(file_abspath).exists():
            raise FileNotFoundError(f"找不到数据文件: {file_abspath}")

        df = pd.read_csv(file_abspath)

        # 数据基础检查
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"数据缺少必要列: {missing_columns}")

        # 数据清理
        df = df.dropna(subset=required_columns)

        # 确保数值类型正确
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 生成信号
        logger.info("开始生成交易信号")
        df = dbb_entry_long_strategy_backtest(df)
        df = dbb_exist_strategy_for_backtest(df)

        # 检查信号生成是否成功
        if 'entry_sig' not in df.columns or 'sell_sig' not in df.columns:
            raise ValueError("信号生成失败，缺少必要的信号列")

        # 转换日期时间
        df['datetime'] = pd.to_datetime(df['datetime'])

        # 按时间排序
        df = df.sort_values('datetime')

        # 检查数据连续性
        time_diff = df['datetime'].diff()
        if time_diff.max().total_seconds() > interval_to_seconds(interval) * 2:
            logger.warning(f"数据可能存在缺失，最大时间间隔: {time_diff.max()}")

        # 打印基本统计信息
        logger.info(f"数据统计:")
        logger.info(f"数据范围: {df['datetime'].min()} 到 {df['datetime'].max()}")
        logger.info(f"总数据条数: {len(df)}")

        # 打印信号统计
        total_entry_signals = df['entry_sig'].sum()
        total_sell_signals = df['sell_sig'].sum()
        logger.info(f"信号统计:")
        logger.info(f"总买入信号数: {total_entry_signals}")
        logger.info(f"总卖出信号数: {total_sell_signals}")

        # 验证信号的有效性
        if total_entry_signals == 0:
            logger.warning("没有检测到买入信号")
        if total_sell_signals == 0:
            logger.warning("没有检测到卖出信号")

        return df

    except pd.errors.EmptyDataError:
        logger.error(f"数据文件为空: {file_abspath}")
        raise
    except pd.errors.ParserError as e:
        logger.error(f"数据文件解析错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理数据时发生错误: {str(e)}")
        raise


def interval_to_seconds(interval: Interval) -> int:
    """
    将时间间隔转换为秒数

    Args:
        interval: 时间间隔枚举

    Returns:
        int: 对应的秒数
    """
    interval_map = {
        Interval.in_1_minute: 60,
        Interval.in_3_minute: 180,
        Interval.in_5_minute: 300,
        Interval.in_15_minute: 900,
        Interval.in_30_minute: 1800,
        Interval.in_45_minute: 2700,
        Interval.in_1_hour: 3600,
        Interval.in_2_hour: 7200,
        Interval.in_3_hour: 10800,
        Interval.in_4_hour: 14400,
        Interval.in_daily: 86400,
        Interval.in_weekly: 604800,
        Interval.in_monthly: 2592000,
    }
    return interval_map.get(interval, 86400)  # 默认返回日线的秒数


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
