from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.dao.account_balance import AccountBalance
from backend.data_center.data_object.dao.auto_trade_config import AutoTradeConfig

okx = OKXAPIWrapper()
account = okx.account


def list_account_balance():
    # 1. 更新现有记录
    response = account.get_account_balance()
    if response.get('code') == '200':
        AccountBalance.insert_or_update(response)

    # 2. 获取列表结果并转换为可修改的字典列表
    balance_list = [dict(balance) for balance in AccountBalance.list_all()]

    # 3. 为每个余额添加自动交易配置
    for balance in balance_list:
        ccy = balance.get('ccy')
        auto_config_list = AutoTradeConfig.list_by_ccy(ccy)
        balance['auto_config_list'] = list(auto_config_list) if auto_config_list else []

    print("Final balance list:", balance_list)
    return balance_list


def list_balance_config(ccy):
    print(AutoTradeConfig.list_by_ccy(ccy))


if __name__ == '__main__':
    list_account_balance()
    # print(list_balance_config("BTC"))
