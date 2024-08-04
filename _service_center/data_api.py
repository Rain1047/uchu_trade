import time
import okx.MarketData as MarketData
import pandas as pd


class MarketAPIWrapper:
    _instance = None

    def __new__(cls, flag):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.market_data_api = MarketData.MarketAPI(flag=flag)
        return cls._instance


def query_candles_with_time_frame(trading_pair: str, flag: str, time_frame: str) -> pd.DataFrame:
    """
    Query historical candlestick data for a given trading pair and time frame.

    Args:
    trading_pair (str): Trading pair symbol.
    flag (str): Flag indicating whether it's for live trading (0) or paper trading (1).
    time_frame (str): Time frame for the candlesticks.

    Returns:
    dict: Historical candlestick data.
    """

    # Get the current millisecond-level timestamp
    millis_timestamp = int(time.time() * 1000)

    # Get historical candlestick data for the trading pair
    result = MarketAPIWrapper(flag).market_data_api.get_candlesticks(
        instId=trading_pair,
        bar=time_frame
    )

    # Define column names
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']

    # Create DataFrame
    df = pd.DataFrame(result['data'], columns=columns)[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    # Convert timestamp to datetime
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Convert other columns to numeric
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

    # Revert the frame
    df = df.iloc[::-1]

    return df

