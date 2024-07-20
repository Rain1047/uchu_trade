import yfinance as yf

from _utils.utils import DateUtils, CheckUtils


class TickerPriceCollector:
    def __init__(self, ticker_symbol, start_date=None, end_date=None):
        self.ticker_symbol = ticker_symbol
        self.start_date = start_date
        self.end_date = end_date

    def get_ticker_price(self):
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


if __name__ == '__main__':
    # Example usage for BTC
    btc_collector = TickerPriceCollector("BTC-USD")
    btc_price = btc_collector.get_ticker_price()
    print(btc_price)
