import logging
from typing import List, Dict, Any

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.enum_obj import EnumAlgoOrdType, EnumTradeEnv, EnumTdMode, EnumOrdType
from backend.data_center.data_object.res.strategy_execute_result import StrategyExecuteResult
from backend.data_center.kline_data.kline_data_reader import KlineDataReader

kline_reader = KlineDataReader()
okx = OKXAPIWrapper(env=EnumTradeEnv.MARKET.value)
trade = okx.trade_api
account = okx.account_api


# 取消永续合约的委托
def cancel_swap_unfinished_algo_order(swap_unfinished_algo_list):
    cancel_algo_list = []
    for algo_order in swap_unfinished_algo_list:
        cancel_algo_list.append(
            {
                'instId': algo_order.get('instId'),
                'algoId': algo_order.get('algoId')
            }
        )
    trade.cancel_algo_order(cancel_algo_list)


# 获取合约未完成的限价止盈委托
def get_swap_limit_order_list() -> List[Dict[str, Any]]:
    swap_limit_orders = trade.get_order_list(
        instType='SWAP', ordType='limit')
    print(swap_limit_orders)
    if swap_limit_orders.get('code') == '0':
        return swap_limit_orders.get('data')
    return []


# 查看永续合约持仓信息
def list_swap_positions() -> List[Dict[str, Any]]:
    # swap_positions = account.get_positions(instType='SWAP')
    swap_positions = account.get_positions()
    print(swap_positions)
    if swap_positions.get('code') == '0':
        return swap_positions.get('data')
    return []


# 获取合约未完成的止盈止损委托
def list_swap_unfinished_algo_order() -> List[Dict[str, Any]]:
    """
    获取未完成的现货算法订单列表

    Returns:
        List[Dict[str, Any]]: 订单列表，如果没有订单或发生错误则返回空列表
    """
    try:
        swap_algo_orders = trade.order_algos_list(
            instType='SWAP',
            ordType=EnumAlgoOrdType.CONDITIONAL_OCO.value
        )
        print(swap_algo_orders)

        # 检查result和data是否存在且有效
        data = swap_algo_orders.get('data')
        if swap_algo_orders.get('code') == '0' and data and isinstance(data, list):
            return data

        return []

    except Exception as e:
        # 记录错误日志
        logging.error(f"获取算法订单列表失败: {str(e)}")
        return []


def place_order(st_result: StrategyExecuteResult):
    # 现货模式限价单
    place_order_result = trade.place_order(
        instId=st_result.symbol,
        tdMode=EnumTdMode.ISOLATED.value,
        side=st_result.side,
        ordType=EnumOrdType.MARKET.value,
        # px="2.15",  # 委托价格
        sz=st_result.sz,  # 委托数量
        slTriggerPx=st_result.stop_loss_price,
        slOrdPx="-1"  # 委托价格为-1时，执行市价止损
    )
    print(place_order_result)


def _save_place_order_record(st_result: StrategyExecuteResult):
    pass


def _save_place_algo_order_record(st_result: StrategyExecuteResult):
    pass


def order_algos_history():
    return trade.order_algos_history(
        orderType=EnumAlgoOrdType.CONDITIONAL_OCO.value,
        instType='SWAP',
        state='effective'
    )


def get_positions_history():
    return account.get_positions_history(instType='SWAP', mgnMode='isolated', type='2')

def place_algo_order(st_result: StrategyExecuteResult):
    place_algo_order_result = trade.place_algo_order(
        instId="ETH-USDT",
        tdMode="cash",
        side="sell",
        ordType="conditional",
        sz="1",
        tpTriggerPx="",
        tpOrdPx="",
        slTriggerPx="2400",
        slOrdPx="2300"
    )
    print(place_algo_order_result)


if __name__ == '__main__':
    # print(result)
    # # 永续合约的限价委托
    # get_swap_limit_order_list()

    # 合约市价下单
    # result = trade.place_order(
    #     instId="ETH-USDT-SWAP",
    #     tdMode="isolated",
    #     side="buy",
    #     posSide="long",
    #     ordType="market",
    #     # px="2.15",  # 委托价格
    #     sz="200",  # 委托数量
    #     slTriggerPx="100",
    #     slOrdPx="90"
    # )
    # print(result)
    #
    # # 永续合约持仓信息
    # list_swap_positions()
    #
    # 交易历史订单
    # print(order_algos_history())

    print(get_positions_history())

    # result = okx_demo.trade.place_algo_order(
    #     instId="ETH-USDT",
    #     tdMode="cash",
    #     side="sell",
    #     ordType="conditional",
    #     sz="1",
    #     tpTriggerPx="",
    #     tpOrdPx="",
    #     slTriggerPx="2400",
    #     slOrdPx="2300"
    # )
    # print(result)
    # # 未完成的永续合约止盈止损委托
    # result = list_swap_unfinished_algo_order()
