import logging
from typing import Dict, Any, List

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.dao.account_balance import AccountBalance
from backend.data_center.data_object.dao.auto_trade_config import AutoTradeConfig
from backend.data_center.data_object.enum_obj import EnumAlgoOrdType, EnumTdMode

okx = OKXAPIWrapper()
trade = okx.trade_api


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


# 取消现货所有未完成的止盈止损委托
def cancel_spot_unfinished_algo_order(algo_orders):
    cancel_result = trade.cancel_algo_order(algo_orders)
    print(cancel_result)


def place_spot_algo_order():
    # 1. 获取configs
    auto_trade_configs = AutoTradeConfig().list_all()
    print(auto_trade_configs)
    # 2. 根据configs组装参数
    for config in auto_trade_configs:
        # post_request = {
        #     'instId': f"{config.get('ccy')}-USDT"
        # }
        if config.get('type') == 'stop_loss':
            result = trade.place_algo_order(
                instId=f"{config.get('ccy')}-USDT",
                tdMode=EnumTdMode.CASH.value,
                side="sell",
                ordType=EnumAlgoOrdType.CONDITIONAL.value,
                sz='100',
                slTriggerPx='0.15',  # 止损触发价格
                slOrdPx='-1'
            )
            print(result)


if __name__ == '__main__':
    # spot_unfinished_algo_list = list_spot_unfinished_algo_order()
    # cancel_algo_list = []
    # for algo_order in spot_unfinished_algo_list:
    #     cancel_algo_list.append(
    #         {
    #             'instId': algo_order.get('instId'),
    #             'algoId': algo_order.get('algoId')
    #         }
    #     )
    # cancel_spot_unfinished_algo_order(cancel_algo_list)

    place_spot_algo_order()




