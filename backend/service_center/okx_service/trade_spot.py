import logging
from typing import Dict, Any, List, Optional

import pandas as pd

from backend._utils import PriceUtils, FormatUtils, SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_processor import KlineDataProcessor
from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center._object_dao.spot_trade_config import SpotTradeConfig
from backend.object_center.enum_obj import EnumAlgoOrdType, EnumTdMode, EnumOrdType, EnumSide
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.service_center.okx_service.ticker_price_service import TickerPriceCollector

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


def list_account_balance():
    # 2. 获取列表结果并转换为可修改的字典列表
    balance_list = [dict(balance) for balance in AccountBalance.list_all()]

    # 3. 通过币种获取自动交易配置
    for balance in balance_list:
        ccy = balance.get('ccy')
        auto_config_list = SpotTradeConfig.list_by_ccy_and_type(ccy)
        balance['auto_config_list'] = list(auto_config_list) if auto_config_list else []

    print("Final balance list:", balance_list)
    return balance_list





if __name__ == '__main__':
    # test_limit_order(trade_pair='ETH-USDT', position="1000")

    # success = SavingBalance.reset(funding.get_saving_balance())
    # print(f"Reset successful: {success}")

    # okx_purchase_redempt(ccy='USDT')
    #
    # reset_account_balance()
    # list_account_balance()

    okx_get_real_account_balance(ccy='USDT')

