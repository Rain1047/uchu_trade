import talib as ta
from pandas import DataFrame


class IndicatorWrapper:

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
        df['adx'] = ta.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14).round(2)

        # SMA Indicator
        SMA_PERIODS = [10, 20, 50, 100, 200]
        for period in SMA_PERIODS:
            df[f'sma{period}'] = ta.SMA(df['close'].values, timeperiod=period).round(2)

        return df




