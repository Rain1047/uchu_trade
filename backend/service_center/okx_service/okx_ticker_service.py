import pandas as pd

from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_processor import KlineDataProcessor
from backend.data_object_center.enum_obj import EnumTimeFrame
from backend._utils import CheckUtils, DateUtils, FormatUtils, SymbolFormatUtils
import yfinance as yf

okx = OKXAPIWrapper()


class OKXTickerService:
    def __init__(self, start_date=None, end_date=None, time_frame=None):
        self.start_date = start_date if start_date is not None else DateUtils.past_time2string(30)
        self.end_date = end_date if start_date is not None else DateUtils.current_time2string()
        self.time_frame = time_frame if time_frame is not None else EnumTimeFrame.H4_U.value
        self.okx = OKXAPIWrapper()
        self.market = OKXAPIWrapper().market_api

    def get_ticker_price_history(self, instId: str):
        ticker_data = yf.Ticker(instId)
        if CheckUtils.is_not_empty(self.start_date) and CheckUtils.is_not_empty(self.end_date):
            ticker_history = ticker_data.history(start=self.start_date, end=self.end_date)
        else:
            print("get past 30 day ticker price")
            ticker_history = self.get_past30day_ticker_price(instId=instId)
        return ticker_history

    @staticmethod
    def get_past30day_ticker_price(instId: str):
        ticker_data = yf.Ticker(instId)
        return ticker_data.history(
            start=DateUtils.past_time2string(30),
            end=DateUtils.current_time2string())

    @staticmethod
    def get_current_ticker_price(instId: str):
        # 获取单个产品行情信息
        return okx.market.get_ticker(instId=instId)['data'][0]['last']

    def get_target_indicator_latest_price(self, instId: str, bar: str, indicator: str, indicator_val: str):
        df = self.query_candles_with_time_frame(instId=instId, bar=bar)
        df = KlineDataProcessor.add_target_indicator(df, indicator=indicator, indicator_val=indicator_val)
        return df.iloc[-1][indicator]

    def get_target_indicator_latest_price_by_spot_config(self, config: dict):
        return self.get_target_indicator_latest_price(
            instId=SymbolFormatUtils.get_usdt(config.get('ccy')),
            bar='1D',
            indicator=config.get('indicator'),
            indicator_val=config.get('indicator_val')
        )

    def get_target_indicator_price(self, instId: str, indicator: str):
        pass

    def query_candles_with_indicators(self, instId: str, bar: str, indicator: str):
        pass

    def query_candles_with_time_frame(self, instId: str, bar: str) -> pd.DataFrame:
        result = self.market.get_candlesticks(
            instId=instId,
            bar=bar,
            limit="300"
        )
        return FormatUtils.dict2df(result)

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
        try:
            # 验证输入参数
            position_float = float(position)
            if pd.isna(position_float) or position_float <= 0:
                print(f"get_sz: invalid position {position}, returning 0")
                return "0"
            
            instId = SymbolFormatUtils.get_swap_usdt(instId)
            last_price = self.get_current_ticker_price(instId)
            
            # 验证价格
            if not last_price or pd.isna(float(last_price)) or float(last_price) <= 0:
                print(f"get_sz: invalid price {last_price}, returning 0")
                return "0"
            
            result = okx.public_data.get_convert_contract_coin(
                instId=instId, px=last_price, sz=position)
            print(result)

            # 验证返回结果
            if not result or 'data' not in result or not result['data'] or len(result['data']) == 0:
                print(f"get_sz: empty result from API, returning 0")
                return "0"
            
            sz_value = result['data'][0]['sz']
            
            # 验证sz值
            if not sz_value or pd.isna(float(sz_value)) or float(sz_value) <= 0:
                print(f"get_sz: invalid sz value {sz_value}, returning 0")
                return "0"
            
            return sz_value
            
        except (ValueError, TypeError, KeyError, IndexError) as e:
            print(f"get_sz: error occurred: {str(e)}, returning 0")
            return "0"
        except Exception as e:
            print(f"get_sz: unexpected error: {str(e)}, returning 0")
            return "0"


if __name__ == '__main__':
    # Example usage for BTC
    collector = OKXTickerService()
    print(OKXTickerService.get_current_ticker_price("ETH-USDT"))

    # current_btc_price = btc_collector.get_current_ticker_price()
    # print(current_btc_price)

    # print(collector.query_candles_with_time_frame(instId="ETH-USDT", bar="4H"))

    # btc_price_history = btc_collector.get_ticker_price_history()
    # print(btc_price_history)
