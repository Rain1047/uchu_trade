from typing import Optional
import pandas as pd
from pandas import DataFrame
from backend.data_center.data_object.dto.strategy_instance import StrategyInstance
from backend.strategy_center.atom_strategy.strategy_registry import registry


@registry.register("dbb_exist_long_strategy")
def dbb_exist_long_strategy(df: DataFrame, stIns: Optional[StrategyInstance]):
    """
    Main entry point for the exit strategy.
    Handles both backtest and live trading modes.
    """
    if stIns is None:
        return dbb_exist_strategy_for_backtest(df)
    return dbb_exist_strategy_for_live(df, stIns)


@registry.register("dbb_exist_strategy_for_live")
def dbb_exist_strategy_for_live(df: DataFrame, stIns: StrategyInstance):
    """
    Live trading implementation of the exit strategy.
    Currently returns the backtest implementation.
    TODO: Implement live trading specific logic
    """
    return dbb_exist_strategy_for_backtest(df)


@registry.register("dbb_exist_strategy_for_backtest")
def dbb_exist_strategy_for_backtest(df: DataFrame) -> DataFrame:
    """
    Backtest implementation of the exit strategy.
    """
    if df.empty:
        return df

    df['sell_sig'] = 0
    df['sell_price'] = df['sma20']

    for i in range(1, len(df)):
        if df.iloc[:i]['entry_sig'].sum() == 0:
            continue

        last_buy_idx = df.iloc[:i][df.iloc[:i]['entry_sig'] == 1].index[-1]
        segment = df.loc[last_buy_idx:df.index[i]]

        if segment['sell_sig'].sum() > 0:
            continue

        if (segment['close'] > segment['upper_band2']).any():
            df.loc[df.index[i], 'sell_price'] = df.loc[df.index[i - 1], 'upper_band1']
        else:
            df.loc[df.index[i], 'sell_price'] = df.loc[df.index[i - 1], 'sma20']

        current_close = df.loc[df.index[i], 'close']
        current_sell_price = df.loc[df.index[i], 'sell_price']

        if pd.notna(current_sell_price):
            df.loc[df.index[i], 'sell_sig'] = 1 if current_close < current_sell_price else 0

    return df
