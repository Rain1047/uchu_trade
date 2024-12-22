from typing import Optional

from pandas import DataFrame

from backend.data_object_center.st_instance import StrategyInstance
from backend.strategy_center.atom_strategy.strategy_registry import registry


@registry.register(name="sma_perfect_order_filter_strategy", desc="SMA完美买卖过滤策略", side="long", type="filter")
def sma_perfect_order_filter_strategy(df: DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return sma_perfect_order_filter_strategy_backtest(df)
    else:
        return sma_perfect_order_filter_strategy_live(df)


def sma_perfect_order_filter_strategy_live(df) -> bool:
    if not df.empty:
        # Calculate differences for last two rows only
        last_two_rows = df.tail(2).copy()
        last_two_rows['sma10_diff_sma20'] = last_two_rows['sma10'] - last_two_rows['sma20']
        last_two_rows['prev_sma10_diff_sma20_1'] = last_two_rows['sma10_diff_sma20'].shift(1)

        # Get the last row's condition
        last_row = last_two_rows.iloc[-1]
        return last_row['sma10_diff_sma20'] > last_row['prev_sma10_diff_sma20_1']
    return False


def sma_perfect_order_filter_strategy_backtest(df: DataFrame) -> DataFrame:
    if not df.empty:
        df['sma10_diff_sma20'] = df['sma10'] - df['sma20']
        df['prev_sma10_diff_sma20_1'] = df['sma10_diff_sma20'].shift(1)
        buy_mask = df['sma10_diff_sma20'] > df['prev_sma10_diff_sma20_1']
        df.loc[~buy_mask, 'entry_sig'] = 0
        df.drop(['sma10_diff_sma20', 'prev_sma10_diff_sma20_1'], axis=1, inplace=True)
    return df
