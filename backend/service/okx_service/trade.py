import logging
from typing import Dict, Any, List

import pandas as pd

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.dao.account_balance import AccountBalance
from backend.data_center.data_object.dao.auto_trade_config import AutoTradeConfig
from backend.data_center.data_object.enum_obj import EnumAlgoOrdType, EnumTdMode
from backend.data_center.kline_data.kline_data_reader import KlineDataReader

kline_reader = KlineDataReader()
okx = OKXAPIWrapper()
trade = okx.trade_api


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
        result = trade.get_order_algos_list(
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
    algo_order_configs = AutoTradeConfig().list_all()
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
    pass


def place_spot_stop_loss_by_config(stop_loss_configs: List):
    for config in stop_loss_configs:
        if config.get('type') == 'stop_loss':
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


if __name__ == '__main__':
    pass

