from pandas import DataFrame

from pandas import DataFrame
import numpy as np


def dbb_strategy_for_backtest(df: DataFrame) -> DataFrame:
    if df.empty:
        return df

    df['prev_close'] = df['close'].shift(1)
    df['stop_loss_price'] = np.nan

    # Case 1: 处于低位盘整
    mask1 = (df['prev_close'] < df['upper_band1']) & (df['close'] < df['upper_band1'])
    df.loc[mask1, 'stop_loss_price'] = df['close']

    # Case 2: 突破第一个band，入场了，止损设置为中间线
    mask2 = (df['prev_close'] < df['upper_band1']) & (df['close'] > df['upper_band1']) & (
            df['close'] < df['upper_band2'])
    df.loc[mask2, 'stop_loss_price'] = df['sma20']

    # Case 3: 突破第二个band，价格走高了，跳高退出线
    mask3 = (df['prev_close'] < df['upper_band2']) & (df['close'] > df['upper_band2'])
    df.loc[mask3, 'stop_loss_price'] = df['upper_band1']

    # Case 4: 高位运行，持续走高，动态移动止损线
    mask4 = (df['prev_close'] > df['upper_band2']) & (df['close'] > df['upper_band2'])
    df.loc[mask4, 'stop_loss_price'] = df['upper_band1']

    # Case 5: 回落，按照upper_band1执行退出
    mask5 = (df['prev_close'] > df['upper_band2']) & (df['close'] < df['upper_band2'])
    df.loc[mask5, 'stop_loss_price'] = df['upper_band1']

    # Forward fill any NaN values
    df['stop_loss_price'].fillna(method='ffill', inplace=True)

    # Drop temporary column
    df.drop('prev_close', axis=1, inplace=True)

    return df
