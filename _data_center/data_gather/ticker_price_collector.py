import yfinance as yf

from _utils.utils import DateUtils, CheckUtils
import okx.MarketData as MarketData
import requests


class TickerPriceCollector:
    def __init__(self, ticker_symbol, start_date=None, end_date=None):
        self.ticker_symbol = ticker_symbol
        self.start_date = start_date
        self.end_date = end_date

    def get_ticker_price_history(self):
        ticker_data = yf.Ticker(self.ticker_symbol)
        if CheckUtils.is_not_empty(self.start_date) and CheckUtils.is_not_empty(self.end_date):
            ticker_history = ticker_data.history(start=self.start_date, end=self.end_date)
        else:
            ticker_history = self.get_past30day_ticker_price()
        return ticker_history

    def get_past30day_ticker_price(self):
        ticker_data = yf.Ticker(self.ticker_symbol)
        return ticker_data.history(
            start=DateUtils.past_time2string(30),
            end=DateUtils.current_time2string())

    def get_current_ticker_price(self):
        flag = "0"  # 实盘:0 , 模拟盘：1
        marketDataAPI = MarketData.MarketAPI(flag=flag)
        if self.ticker_symbol.endswith("-USD") or self.ticker_symbol.endswith("-USDT"):
            # 获取单个产品行情信息
            result = marketDataAPI.get_ticker(
                instId=self.ticker_symbol[:-4] + "-USDT-SWAP"
            )['data'][0]['last']
            return result
        elif self.ticker_symbol.endswith("-USD-SWAP"):
            return marketDataAPI.get_ticker(instId=self.ticker_symbol)['data'][0]['last']


if __name__ == '__main__':
    # Example usage for BTC
    btc_collector = TickerPriceCollector("BTC-USD")

    current_btc_price = btc_collector.get_current_ticker_price()
    print(current_btc_price)

    btc_price_history = btc_collector.get_ticker_price_history()
    print(btc_price_history)
