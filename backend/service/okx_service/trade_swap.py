import logging
from typing import List, Dict, Any

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.enum_obj import EnumAlgoOrdType, EnumTradeEnv
from backend.data_center.kline_data.kline_data_reader import KlineDataReader

kline_reader = KlineDataReader()
okx = OKXAPIWrapper(env=EnumTradeEnv.DEMO.value)
trade = okx.trade_api
account = okx.account


def get_swap_order(instId=''):
    print(trade.get_order(instId=instId))


def get_swap_order_list(instType):
    print(trade.get_order_list(instType=instType))


# 查看持仓信息
def list_swap_positions():
    result = account.get_positions(instType='SWAP')
    print(result)


def list_spot_unfinished_algo_order() -> List[Dict[str, Any]]:
    """
    获取未完成的现货算法订单列表

    Returns:
        List[Dict[str, Any]]: 订单列表，如果没有订单或发生错误则返回空列表
    """
    try:
        result = trade.order_algos_list(
            # instType='SWAP',
            # ordType=EnumAlgoOrdType.CONDITIONAL.value
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


if __name__ == '__main__':
    # result = list_spot_unfinished_algo_order()
    # print(result)
    # list_swap_positions()
    get_swap_order_list(instType='SWAP')
