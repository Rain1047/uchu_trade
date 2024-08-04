from datetime import time

import yfinance as yf
import pandas as pd

from _service_center.data_api import MarketAPIWrapper
from _utils.utils import *
import okx.MarketData as MarketData
from _service_center._okx_service.okx_api import OKXAPIWrapper
from _data_center.data_object.enum_obj import *
import requests

okx = OKXAPIWrapper()


class TickerPriceCollector:
    def __init__(self, instId, start_date=None, end_date=None, time_frame=None):
        self.instId = instId
        self.start_date = start_date if start_date is not None else DateUtils.past_time2string(30)
        self.end_date = end_date if start_date is not None else DateUtils.current_time2string()
        self.time_frame = time_frame if time_frame is not None else EnumTimeFrame.H4_U.value

    def get_ticker_price_history(self):
        ticker_data = yf.Ticker(self.ticker_symbol)
        if CheckUtils.is_not_empty(self.start_date) and CheckUtils.is_not_empty(self.end_date):
            ticker_history = ticker_data.history(start=self.start_date, end=self.end_date)
        else:
            print("get past 30 day ticker price")
            ticker_history = self.get_past30day_ticker_price()
        return ticker_history

    def get_past30day_ticker_price(self):
        ticker_data = yf.Ticker(self.ticker_symbol)
        return ticker_data.history(
            start=DateUtils.past_time2string(30),
            end=DateUtils.current_time2string())

    def get_current_ticker_price(self):
        if self.ticker_symbol.endswith("-USD") or self.ticker_symbol.endswith("-USDT"):
            # # 获取单个产品行情信息
            result = okx.get_ticker(
                instId=self.ticker_symbol[:-4] + "-USDT-SWAP")['data'][0]['last']
            return result
        elif self.ticker_symbol.endswith("-USD-SWAP"):
            return okx.get_ticker(instId=self.ticker_symbol)['data'][0]['last']

    def query_candles_with_time_frame(self, bar: str) -> pd.DataFrame:

        # Get historical candlestick data for the trading pair
        # result = MarketAPIWrapper(flag).market_data_api.get_candlesticks(
        #     instId=trading_pair,
        #     bar=time_frame
        # )
        result = okx.get_candlesticks(
            instId=self.instId,
            bar=bar
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


if __name__ == '__main__':
    # Example usage for BTC
    btc_collector = TickerPriceCollector("BTC-USD")

    # current_btc_price = btc_collector.get_current_ticker_price()
    # print(current_btc_price)

    print(btc_collector.query_candles_with_time_frame(bar="4H"))

    # btc_price_history = btc_collector.get_ticker_price_history()
    # print(btc_price_history)
