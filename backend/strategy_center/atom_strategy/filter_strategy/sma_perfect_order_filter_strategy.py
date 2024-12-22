from typing import Optional

from pandas import DataFrame

from backend.data_object_center.st_instance import StrategyInstance
from backend.strategy_center.atom_strategy.strategy_registry import registry


@registry.register(name="sma_perfect_order_filter_strategy", desc="SMA标准排序过滤策略", side="long", type="filter")
def sma_perfect_order_filter_strategy(df: DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return sma_perfect_order_filter_strategy_backtest(df)
    else:
        return sma_perfect_order_filter_strategy_live(df)


def sma_perfect_order_filter_strategy_live(df: DataFrame) -> bool:
    if not df.empty:
        last_row = df.iloc[-1]
        return (last_row['sma10'] > last_row['sma20']) and (last_row['sma20'] > last_row['sma50'])
    return False


def sma_perfect_order_filter_strategy_backtest(df: DataFrame) -> DataFrame:
    if not df.empty:
        buy_mask = (df['sma10'] > df['sma20']) & (df['sma20'] > df['sma50'])
        df.loc[~buy_mask, 'entry_sig'] = 0
    return df
