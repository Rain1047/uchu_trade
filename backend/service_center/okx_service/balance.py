import logging

from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend._constants import okx_constants
from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center._object_dao.spot_trade_config import SpotTradeConfig

logger = logging.getLogger(__name__)
okx = OKXAPIWrapper()
account = okx.account


def list_account_balance():
    # 1. 更新现有记录
    response = account.get_account_balance()
    print(response)
    if response.get('code') == okx_constants.SUCCESS_CODE:
        AccountBalance.insert_or_update(response)
    else:
        print(response)
        logger.error(f"list_account_balance error, response: {response.get('code')}, {response.get('message')}")

    # 2. 获取列表结果并转换为可修改的字典列表
    balance_list = [dict(balance) for balance in AccountBalance.list_all()]

    # 3. 通过币种获取自动交易配置
    for balance in balance_list:
        ccy = balance.get('ccy')
        auto_config_list = SpotTradeConfig.list_by_ccy_and_type(ccy)
        balance['auto_config_list'] = list(auto_config_list) if auto_config_list else []

    print("Final balance list:", balance_list)
    return balance_list


def reset_account_balance():
    # 1. 更新现有记录
    response = account.get_account_balance()
    if response.get('code') == okx_constants.SUCCESS_CODE:
        AccountBalance.reset_account_balance(response)
    else:
        print(response)
        logger.error(f"list_account_balance error, response: {response.get('code')}, {response.get('message')}")

    # 2. 获取列表结果并转换为可修改的字典列表
    balance_list = [dict(balance) for balance in AccountBalance.list_all()]

    # 3. 通过币种获取自动交易配置
    for balance in balance_list:
        ccy = balance.get('ccy')
        auto_config_list = SpotTradeConfig.list_by_ccy_and_type(ccy)
        balance['auto_config_list'] = list(auto_config_list) if auto_config_list else []

    print("Final balance list:", balance_list)
    return balance_list


def list_balance_config(ccy):
    print(SpotTradeConfig.list_by_ccy_and_type(ccy))


if __name__ == '__main__':
    # list_account_balance()
    # print(list_balance_config("BTC"))
    reset_account_balance()
