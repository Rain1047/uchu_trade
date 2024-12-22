import pandas as pd
from backend.backtest_center.backtest_core.backtest_system import BacktestSystem
from backend.data_object_center.enum_obj import get_interval_by_value
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.data_object_center.st_instance import StrategyInstance
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import registry


def backtest_main(st_instance_id):
    """主函数"""
    # 创建回测系统实例
    backtest = BacktestSystem(initial_cash=100000.0, risk_percent=2.0, commission=0.001)

    # get strategy instance
    st = StrategyInstance.get_st_instance_by_id(st_instance_id)
    interval = get_interval_by_value(st.time_frame)
    # 准备数据
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol=st.trade_pair.split('-')[0], interval=interval)
    df = pd.read_csv(f"{file_abspath}")

    # 执行策略生成信号
    entry_strategy = registry.get_strategy(st.entry_st_code)
    df = entry_strategy(df, None)
    exist_strategy = registry.get_strategy(st.exit_st_code)
    df = exist_strategy(df, None)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[df['datetime'] > "2023-12-31 08:00:00"]

    # 运行回测
    return backtest.run(df, plot=True, st=st)


if __name__ == '__main__':
    backtest_main(8)

