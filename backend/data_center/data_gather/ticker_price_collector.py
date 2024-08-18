from typing import Optional

import yfinance as yf

from backend.service.okx_service import OKXAPIWrapper
from backend.data_center.data_object.enum_obj import *
from backend.service.utils import *

okx = OKXAPIWrapper()


class TickerPriceCollector:
    def __init__(self, start_date=None, end_date=None, time_frame=None):
        self.start_date = start_date if start_date is not None else DateUtils.past_time2string(30)
        self.end_date = end_date if start_date is not None else DateUtils.current_time2string()
        self.time_frame = time_frame if time_frame is not None else EnumTimeFrame.H4_U.value

    def get_ticker_price_history(self, instId: str):
        ticker_data = yf.Ticker(instId)
        if CheckUtils.is_not_empty(self.start_date) and CheckUtils.is_not_empty(self.end_date):
            ticker_history = ticker_data.history(start=self.start_date, end=self.end_date)
        else:
            print("get past 30 day ticker price")
            ticker_history = self.get_past30day_ticker_price()
        return ticker_history

    @staticmethod
    def get_past30day_ticker_price(instId: str):
        ticker_data = yf.Ticker(instId)
        return ticker_data.history(
            start=DateUtils.past_time2string(30),
            end=DateUtils.current_time2string())

    @staticmethod
    def get_current_ticker_price(instId: str):
        # # 获取单个产品行情信息
        if instId.endswith("-USDT"):
            return okx.market.get_ticker(instId=instId)['data'][0]['last']
        else:
            return okx.market.get_ticker(instId=instId+"-USDT")['data'][0]['last']

    @staticmethod
    def query_candles_with_time_frame(instId: str, bar: str) -> pd.DataFrame:

        # Get historical candlestick data for the trading pair
        # result = MarketAPIWrapper(flag).market_data_api.get_candlesticks(
        #     instId=trading_pair,
        #     bar=time_frame
        # )
        result = okx.market.get_candlesticks(
            instId=instId,
            bar=bar
        )
        return FormatUtils.dict2df(result)

    def get_sz(self, instId: str, position: str) -> str:
        # 获取单个产品行情信息
        last_price = self.get_current_ticker_price(instId)
        return okx.publicData.get_convert_contract_coin(
            instId=instId, px=last_price, sz=position)['data'][0]['sz']


if __name__ == '__main__':
    # Example usage for BTC
    collector = TickerPriceCollector()
    print(TickerPriceCollector.get_current_ticker_price("ETH-USDT"))

    # current_btc_price = btc_collector.get_current_ticker_price()
    # print(current_btc_price)

    # print(collector.query_candles_with_time_frame(instId="ETH-USDT", bar="4H"))

    # btc_price_history = btc_collector.get_ticker_price_history()
    # print(btc_price_history)
