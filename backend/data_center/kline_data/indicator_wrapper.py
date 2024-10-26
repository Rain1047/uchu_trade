import talib as ta
import pandas as pd
from pandas import DataFrame
from backend.data_center.kline_data.kline_data_collector import *


class IndicatorWrapper:
    """
    A class to wrap around a DataFrame and add various technical indicators.
    """

    def __init__(self):
        """
        Initialize the IndicatorWrapper without a DataFrame.
        """
        pass

    @staticmethod
    def add_indicator(df: DataFrame) -> DataFrame:
        """
        Add technical indicators to the provided DataFrame.

        :param df: A pandas DataFrame containing OHLC data (open, high, low, close).
        :return: The DataFrame with added technical indicators.
        """
        if 'high' not in df.columns or 'low' not in df.columns or 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'high', 'low', and 'close' columns.")

        # ADX Indicator
        df['adx'] = ta.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)

        # SMA Indicator
        SMA_PERIODS = [10, 20, 50, 100, 200]
        for period in SMA_PERIODS:
            df[f'sma{period}'] = ta.SMA(df['close'].values, timeperiod=period)

        return df


# Example usage:
if __name__ == '__main__':
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_daily)
    df = pd.read_csv(f"{file_abspath}")
    wrapper = IndicatorWrapper()
    df_with_indicators = wrapper.add_indicator(df)
    print(df_with_indicators.head())

