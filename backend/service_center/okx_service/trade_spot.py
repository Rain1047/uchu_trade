import logging
from typing import Dict, Any, List, Optional

import pandas as pd

from backend._constants import okx_constants
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


def cancel_all_algo_orders_main_task():
    spot_unfinished_algo_list = list_spot_unfinished_algo_order()
    cancel_algo_list = []
    for algo_order in spot_unfinished_algo_list:
        cancel_algo_list.append(
            {
                'instId': algo_order.get('instId'),
                'algoId': algo_order.get('algoId')
            }
        )
    cancel_spot_unfinished_algo_order(cancel_algo_list)


# 获取现货所有未完成的止盈止损委托
def list_spot_unfinished_algo_order() -> List[Dict[str, Any]]:
    """
    获取未完成的现货算法订单列表

    Returns:
        List[Dict[str, Any]]: 订单列表，如果没有订单或发生错误则返回空列表
    """
    try:
        result = trade.order_algos_list(
            instType='SPOT',
            ordType=EnumAlgoOrdType.CONDITIONAL_OCO.value
        )

        # 检查result和data是否存在且有效
        data = result.get('data')
        if result.get('code') == '0' and data and isinstance(data, list):
            return data

        return []

    except Exception as e:
        # 记录错误日志
        logging.error(f"获取算法订单列表失败: {str(e)}")
        return []


# 取消现货所有未完成的止盈止损和限价委托
def cancel_spot_unfinished_algo_order(algo_orders):
    cancel_result = trade.cancel_algo_order(algo_orders)
    print(cancel_result)


price_collector = TickerPriceCollector()


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

