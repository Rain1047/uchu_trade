# market_api_wrapper.py

import okx.MarketData as Market
from typing import Dict, Optional
from backend._decorators import add_docstring
from backend._utils import FormatUtils
import pandas as pd


class MarketAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.marketAPI = Market.MarketAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("通过Ticker Symbol来获取行情")
    def get_ticker(self, instId: str) -> Dict:
        return self.marketAPI.get_ticker(instId=instId)

    @add_docstring("通过Ticker Symbol获取k线")
    def get_candlesticks(self, instId: str, bar: Optional[str] = '1D', limit: Optional[str] = '300') -> Dict:
        return self.marketAPI.get_candlesticks(instId=instId, bar=bar, limit=limit)

    @add_docstring("通过Ticker Symbol获取k线，并返回DataFrame")
    def get_candlesticks_df(self, instId: str, bar: Optional[str] = '1D') -> pd.DataFrame:
        return FormatUtils.dict2df(self.marketAPI.get_candlesticks(instId=instId, bar=bar))
