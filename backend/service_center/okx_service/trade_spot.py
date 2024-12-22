import logging
from typing import Dict, Any, List, Optional

import pandas as pd

from backend._utils import PriceUtils, FormatUtils, SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_processor import KlineDataProcessor
from backend.data_center.kline_data.kline_data_reader import KlineDataReader

logger = logging.getLogger(__name__)
kline_reader = KlineDataReader()
okx = OKXAPIWrapper()
account = okx.account_api
trade = okx.trade_api
market = okx.market_api
funding = okx.funding_api


def query_candles_with_time_frame(instId: str, bar: str) -> pd.DataFrame:
    result = market.get_candlesticks(
        instId=instId,
        bar=bar,
        limit="300"
    )
    return FormatUtils.dict2df(result)


def test_limit_order(trade_pair: str, position: str):
    # current_price = price_collector.get_current_ticker_price(trade_pair)

    df = query_candles_with_time_frame(trade_pair, '1D')
    df = KlineDataProcessor.add_indicator(df)
    print(df)


if __name__ == '__main__':
    # test_limit_order(trade_pair='ETH-USDT', position="1000")

    # success = SavingBalance.reset(funding.get_saving_balance())
    # print(f"Reset successful: {success}")

    # okx_purchase_redempt(ccy='USDT')
    #
    # reset_account_balance()
    # list_account_balance()
    pass
