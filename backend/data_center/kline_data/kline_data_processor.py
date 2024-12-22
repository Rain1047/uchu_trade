import talib as ta
from pandas import DataFrame
import pandas as pd
import numpy as np


class KlineDataProcessor:

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
        df['adx'] = ta.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14).round(6)

        # SMA Indicator
        SMA_PERIODS = [10, 20, 50, 100, 200]
        for period in SMA_PERIODS:
            df[f'sma{period}'] = ta.SMA(df['close'].values, timeperiod=period).round(2)
            df[f'ema{period}'] = ta.EMA(df['close'].values, timeperiod=period).round(2)

        # 布林带 Double Boolean Bands
        df['upper_band1'], _, df['lower_band1'] = ta.BBANDS(df['close'], timeperiod=20, nbdevup=1, nbdevdn=1)
        df['upper_band2'], _, df['lower_band2'] = ta.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)

        return df

    @staticmethod
    def format_result(df: DataFrame) -> DataFrame:
        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume', 'buy_sig', 'sell_sig']].copy()
        df['stop_loss'] = 0.0
        # Rename 'datetime' column to ensure it's in the desired format
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Set the data types for the new DataFrame
        return df.astype({
            'datetime': 'datetime64[ns]',
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'volume': 'int64',  # Change to int64 as specified
            'buy_sig': 'int64',
            'sell_sig': 'int64',
            'stop_loss': 'float64'  # Assuming you want this column as well
        })

    @staticmethod
    def add_target_indicator(df: DataFrame, indicator: str, indicator_val: str) -> DataFrame:
        if 'high' not in df.columns or 'low' not in df.columns or 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'high', 'low', and 'close' columns.")

        # ADX Indicator
        if indicator == 'adx' or indicator == 'ADX':
            df[indicator] = ta.ADX(df['high'].values, df['low'].values, df['close'].values,
                                   timeperiod=int(indicator_val)).round(6)

        # SMA Indicator
        if indicator == 'sma' or indicator == 'SMA':
            df[indicator] = ta.SMA(df['close'].values, timeperiod=int(indicator_val)).round(2)

        # EMA Indicator
        if indicator == 'ema' or indicator == 'EMA':
            df[indicator] = ta.EMA(df['close'].values, timeperiod=int(indicator_val)).round(2)

        # 布林带 Double Boolean Bands
        if indicator == 'upper_band' or indicator == 'UPPER_BAND':
            df[indicator] = ta.BBANDS(df['close'], timeperiod=20, nbdevup=int(indicator_val),
                                      nbdevdn=int(indicator_val))[0].round(2)

        if indicator == 'lower_band' or indicator == 'LOWER_BAND':
            df[indicator] = ta.BBANDS(df['close'], timeperiod=20, nbdevup=int(indicator_val),
                                      nbdevdn=int(indicator_val))[2].round(2)
        return df
