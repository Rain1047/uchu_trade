import yfinance as yf

from _utils.utils import *
from _service_center._okx_service.okx_api import OKXAPIWrapper
from _data_center.data_object.enum_obj import *

okx = OKXAPIWrapper()


class TickerPriceCollector:
    def __init__(self, instId, start_date=None, end_date=None, time_frame=None):
        self.instId = instId
        self.start_date = start_date if start_date is not None else DateUtils.past_time2string(30)
        self.end_date = end_date if start_date is not None else DateUtils.current_time2string()
        self.time_frame = time_frame if time_frame is not None else EnumTimeFrame.H4_U.value

    def get_ticker_price_history(self):
        ticker_data = yf.Ticker(self.instId)
        if CheckUtils.is_not_empty(self.start_date) and CheckUtils.is_not_empty(self.end_date):
            ticker_history = ticker_data.history(start=self.start_date, end=self.end_date)
        else:
            print("get past 30 day ticker price")
            ticker_history = self.get_past30day_ticker_price()
        return ticker_history

    def get_past30day_ticker_price(self):
        ticker_data = yf.Ticker(self.instId)
        return ticker_data.history(
            start=DateUtils.past_time2string(30),
            end=DateUtils.current_time2string())

    def get_current_ticker_price(self):
        if self.instId.endswith("-USD") or self.instId.endswith("-USDT"):
            # # 获取单个产品行情信息
            result = okx.get_ticker(
                instId=self.instId[:-4] + "-USDT-SWAP")['data'][0]['last']
            return result
        elif self.instId.endswith("-USD-SWAP"):
            return okx.get_ticker(instId=self.instId)['data'][0]['last']

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
        return FormatUtils.dict2df(result)


if __name__ == '__main__':
    # Example usage for BTC
    btc_collector = TickerPriceCollector("BTC-USDT")

    # current_btc_price = btc_collector.get_current_ticker_price()
    # print(current_btc_price)

    print(btc_collector.query_candles_with_time_frame(bar="4H"))

    # btc_price_history = btc_collector.get_ticker_price_history()
    # print(btc_price_history)
