from typing import Optional

import pandas as pd
from pandas import DataFrame

from backend.data_center.data_object.dto.strategy_instance import StrategyInstance
from backend.strategy_center.atom_strategy.strategy_registry import StrategyRegistry


@StrategyRegistry.register("dbb_exist_long_strategy")
def dbb_exist_long_strategy(df: DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return dbb_exist_strategy_for_backtest(df)
    else:
        return dbb_exist_strategy_for_backtest(df)


@StrategyRegistry.register("dbb_exist_strategy_for_backtest")
def dbb_exist_strategy_for_backtest(df: DataFrame) -> DataFrame:
    if df.empty:
        return df

    df['sell_sig'] = 0  # Default to hold
    df['sell_price'] = df['sma20']

    # 获取上一个buy_sig=1的bar, 并且该之间所有的sell_sig=0
    # 如果未满足说明没有进场或已经卖出, sell_sig=0

    # 如果和上一个buy_sig=1的bar之间存在close>band2, 那么sell_price=prev_band1

    # 如果之间不存在close>band2, 那么sell_price=prev_sma20

    # 如果今天的close<sell_price, 那么sell_sig=1

    # 如果今天的close>sell_price, 那么sell_sig=0

    # 遍历每一行来实现策略逻辑
    for i in range(1, len(df)):
        # 如果当前没有持仓（之前没有buy信号），继续下一个
        if df.iloc[:i]['entry_sig'].sum() == 0:
            continue

        # 获取上一个buy_sig=1的位置
        last_buy_idx = df.iloc[:i][df.iloc[:i]['entry_sig'] == 1].index[-1]

        # 提取从上次买入到现在的片段
        segment = df.loc[last_buy_idx:df.index[i]]

        # 检查是否已经有卖出信号（避免重复处理）
        if segment['sell_sig'].sum() > 0:
            continue

        # 检查区间内是否有close > band2的情况
        if (segment['close'] > segment['upper_band2']).any():
            # 设置卖出价格为前一个band1
            df.loc[df.index[i], 'sell_price'] = df.loc[df.index[i - 1], 'upper_band1']
        else:
            # 设置卖出价格为前一个sma20
            df.loc[df.index[i], 'sell_price'] = df.loc[df.index[i - 1], 'sma20']

        # 根据当前close和sell_price的关系决定是否卖出
        current_close = df.loc[df.index[i], 'close']
        current_sell_price = df.loc[df.index[i], 'sell_price']

        if pd.notna(current_sell_price):  # 确保有卖出价格
            if current_close < current_sell_price:
                df.loc[df.index[i], 'sell_sig'] = 1
            else:
                df.loc[df.index[i], 'sell_sig'] = 0

    return df
