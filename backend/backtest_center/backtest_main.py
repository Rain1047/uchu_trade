import backtrader as bt
import pandas as pd

from tvDatafeed import Interval

from backend.backtest_center.backtest_core.backtest_system import BacktestSystem
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import registry


def main():
    """主函数"""
    # 创建回测系统实例
    backtest = BacktestSystem(initial_cash=100000.0, risk_percent=2.0, commission=0.001)

    # 准备数据
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_4_hour)
    df = pd.read_csv(f"{file_abspath}")

    # 执行策略生成信号
    entry_strategy = registry.get_strategy("dbb_entry_long_strategy")
    df = entry_strategy(df, None)
    exist_strategy = registry.get_strategy("dbb_exist_long_strategy")
    df = exist_strategy(df, None)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[df['datetime'] > "2023-12-31 08:00:00"]

    # 打印生成的信号统计
    total_entry_signals = df['entry_sig'].sum()
    total_sell_signals = df['sell_sig'].sum()
    print(f"\n信号统计:")
    print(f"总买入信号数: {total_entry_signals}")
    print(f"总卖出信号数: {total_sell_signals}")

    # 运行回测
    results = backtest.run(df, plot=True)


if __name__ == '__main__':
    main()

