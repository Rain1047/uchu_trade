import logging
from typing import Dict, Any, List, Optional

import pandas as pd

from backend._constants import okx_constants
from backend._utils import PriceUtils, FormatUtils, SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_processor import KlineDataProcessor
from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center._object_dao.saving_balance import SavingBalance
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


# [调度主任务] 取消所有的限价、止盈止损订单
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


# [调度主任务] 根据配置进行止盈止损、限价委托
def place_algo_order_main_task():
    # 1. 获取configs
    algo_order_configs = SpotTradeConfig().list_all()
    limit_order_configs = []
    stop_loss_configs = []
    for config in algo_order_configs:
        if config.get('type') == 'stop_loss':
            stop_loss_configs.append(config)
        elif config.get('type') == 'limit_order':
            limit_order_configs.append(config)
    # 2. 处理stop loss的任务
    if len(stop_loss_configs) > 0:
        place_spot_stop_loss_by_config(stop_loss_configs)
    # 3. 处理limit order的任务
    if len(limit_order_configs) > 0:
        place_spot_limit_order_by_config(limit_order_configs)


def place_spot_limit_order_by_config(limit_order_configs: List):
    for config in limit_order_configs:
        ccy = config.get('ccy')
        print(ccy)
        balance = AccountBalance().list_by_ccy(config.get('ccy'))
        eq = balance.get('eq')
        interval = config.get('interval')
        pct = config.get('percentage')
        amount = config.get('amount')
        # 通过sig和interval获取价格
        file_abspath = kline_reader.get_abspath(symbol=ccy, interval='1D')
        kline_data = pd.read_csv(f"{file_abspath}")
        target_index = config.get('signal').lower() + interval
        target_price = kline_data.iloc[-1][target_index]
        print(f"{eq},{pct}")
        if pct is not None and str(pct).strip():
            eq = str(round(float(eq) * int(pct) / 100, 6))
            print(eq)
        else:
            eq = '0'

        print(
            {
                'instId': f"{config.get('ccy')}-USDT",
                'tdMode': EnumTdMode.CASH.value,
                'side': "sell",
                'ordType': EnumAlgoOrdType.CONDITIONAL.value,
                'sz': eq,
                'slTriggerPx': str(target_price),  # 止损触发价格
                'slOrdPx': '-1'
            }
        )
        result = trade.place_algo_order(
            instId=f"{config.get('ccy')}-USDT",
            tdMode=EnumTdMode.CASH.value,
            side="sell",
            ordType=EnumAlgoOrdType.CONDITIONAL.value,
            sz=eq,
            slTriggerPx=str()
        )


def place_spot_stop_loss_by_config(stop_loss_configs: List):
    for config in stop_loss_configs:
        ccy = config.get('ccy')
        print(ccy)
        balance = AccountBalance().list_by_ccy(config.get('ccy'))
        eq = balance.get('eq')
        interval = config.get('interval')
        pct = config.get('percentage')
        amount = config.get('amount')
        # 通过sig和interval获取价格
        file_abspath = kline_reader.get_abspath(symbol=ccy, interval='1D')
        kline_data = pd.read_csv(f"{file_abspath}")
        target_index = config.get('signal').lower() + interval
        target_price = kline_data.iloc[-1][target_index]

        print(f"{eq},{pct}")
        if pct is not None and str(pct).strip():
            eq = str(round(float(eq) * int(pct) / 100, 6))
            print(eq)
        else:
            eq = '0'
        print(
            {
                'instId': f"{config.get('ccy')}-USDT",
                'tdMode': EnumTdMode.CASH.value,
                'side': "sell",
                'ordType': EnumAlgoOrdType.CONDITIONAL.value,
                'sz': eq,
                'slTriggerPx': str(target_price),  # 止损触发价格
                'slOrdPx': '-1'
            }
        )
        result = trade.place_algo_order(
            instId=f"{config.get('ccy')}-USDT",
            tdMode=EnumTdMode.CASH.value,
            side="sell",
            ordType=EnumAlgoOrdType.CONDITIONAL.value,
            sz=eq,
            slTriggerPx=str(target_price),  # 止损触发价格
            slOrdPx='-1'
        )
        print(result)


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

    # sz = price_collector.get_sz(instId=trade_pair, position=position)
    # print(f"trade_pair: {trade_pair}, position: {position}, sz: {sz}")
    # result = trade.place_order(
    #     instId=trade_pair,
    #     sz="0.1",  # 委托数量 当instId为ETH时，1代表1个ETH
    #     side=EnumSide.BUY.value,
    #     tdMode=EnumTdMode.CASH.value,
    #     ordType=EnumOrdType.LIMIT.value,
    #     px=position  # 委托价格
    # )
    # print(result)


# okx一键赎回
def okx_purchase_redempt(ccy: Optional[str]):
    try:
        # 1. 重制简单赚币中的币种余额
        reset_saving_balance()
        # 2. 查看币种余额
        ccy = SymbolFormatUtils.get_base_symbol(ccy)
        # 3. 获取金额
        amt = get_saving_balance(symbol=ccy)['loan_amt']
        # 4. 赎回
        funding.purchase_redempt(ccy=ccy, amt=amt)
    except Exception as e:
        print(f"purchase_redempt error: {e}")
        pass


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


def get_saving_balance(symbol: Optional[str] = '') -> dict:
    return SavingBalance().list_by_condition(condition="ccy", value=symbol)[0]


def reset_account_balance():
    # 1. 更新现有记录
    response = account.get_account_balance()
    if response.get('code') == okx_constants.SUCCESS_CODE:
        AccountBalance.reset_account_balance(response)
        return True
    else:
        print(response)
        logger.error(f"list_account_balance error, response: {response.get('code')}, {response.get('message')}")
        return False


def reset_saving_balance() -> bool:
    result = funding.get_saving_balance()
    success = SavingBalance.reset(result)
    return success


if __name__ == '__main__':
    # test_limit_order(trade_pair='ETH-USDT', position="1000")

    # success = SavingBalance.reset(funding.get_saving_balance())
    # print(f"Reset successful: {success}")

    # okx_purchase_redempt(ccy='USDT')

    reset_account_balance()
    list_account_balance()
