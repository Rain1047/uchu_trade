from pandas import DataFrame

from backend.strategy_center.atom_strategy.strategy_registry import StrategyRegistry


@StrategyRegistry.register("sma_perfect_order_filter_strategy")
def sma_perfect_order_filter_strategy(df: DataFrame) -> DataFrame:
    if not df.empty:
        buy_mask = (df['sma10'] > df['sma20']) & (df['sma20'] > df['sma50'])
        df.loc[~buy_mask, 'entry_sig'] = 0
    return df
