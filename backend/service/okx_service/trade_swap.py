import logging
from typing import List, Dict, Any, Optional

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
# def list_swap_positions() -> List[Dict[str, Any]]:
#     # swap_positions = account.get_positions(instType='SWAP')
#     swap_positions = account.get_positions()
#     print(swap_positions)
#     if swap_positions.get('code') == '0':
#         return swap_positions.get('data')
#     return []


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
        state='canceled'
    )


def get_order(insId: str, ordId: Optional[str], clOrdId: Optional[str]):
    return trade.get_order(instId=insId, ordId=ordId, clOrdId=clOrdId)


def amend_order(instId: str, ordId: Optional[str], clOrdId: Optional[str], newSz: Optional[str], newPx: Optional[str],
                newSlTriggerPx: Optional[str],  # 如果止损触发价或者委托价为0，那代表删除止损。
                newSlOrdPx: Optional[str]  # 委托价格为-1时，执行市价止损。
                ):
    return trade.amend_order(instId=instId, ordId=ordId, clOrdId=clOrdId, newSz=newSz, newPx=newPx,
                             newSlTriggerPx=newSlTriggerPx, newSlOrdPx=newSlOrdPx)


# def get_positions_history():
#     return account.get_positions_history(instType='SWAP', mgnMode='isolated', type='2')


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
        slOrdPx="2300",
        algoClOrdId="test_2024_12_07",  # 客户自定义策略订单ID
    )
    print(place_algo_order_result)


if __name__ == '__main__':
    # 1. 下单委托 place_order 市价入场 clOrdId
    # 合约市价下单

    # attachAlgoOrds = [
    #     {
    #         'attachAlgoClOrdId': "testAlgoPlaceOrder12080244",  # 需要唯一
    #         'slTriggerPx': "3995",
    #         'slOrdPx': "-1",
    #     }
    # ]
    #
    # result = trade.place_order(
    #     instId="ETH-USDT-SWAP",
    #     tdMode="isolated",
    #     side="buy",
    #     posSide="long",
    #     ordType="market",
    #     # px="2.15",  # 委托价格
    #     sz="1",  # 委托数量
    #     # slTriggerPx="3995",
    #     # slOrdPx="-1",
    #     clOrdId="testPlaceOrder12080119",
    #     attachAlgoOrds=attachAlgoOrds
    # )
    # # ordId = result.get('data')[0].get('ordId')
    # # print(ordId)
    # print(result)

    # 2. 获取订单 get_order clOrdId
    # 2049761648444694528
    # testPlaceOrder12080041
    result = trade.get_order(instId='ETH-USDT-SWAP', ordId='', clOrdId='testPlaceOrder12080119')
    print(result)

    # 3. 获取策略订单 get_algo_order algoClOrdId <- attachAlgoOrds-attachAlgoClOrdId
    result = trade.get_algo_order(algoId='', algoClOrdId='testAlgoPlaceOrder12080119')
    print(result)
    result = trade.get_algo_order(algoId='', algoClOrdId='testAlgoPlaceOrder12080244')
    print(result)

    # 4. 修改策略止损价
    # result = trade.amend_algo_order(
    #     instId='ETH-USDT-SWAP', algoId='', algoClOrdId='testAlgoPlaceOrder12080244',
    #     newSlTriggerPx='3993', newSlOrdPx='-1'
    # )
    # print(result)

    # 5. 查看过程和结果




    # 3. 修改止损价
    # result = trade.amend_order(instId='ETH-USDT-SWAP', clOrdId='testPlaceOrder12080041', ordId='',
    #                            newSlTriggerPx='200', newSlOrdPx='-1')
    # print(result)

    # 2. 策略止损委托 place_algo_order 止损委托 algoClOrdId
    # 2.1 撤销策略委托 cancel_algo_order algoId

    # # 永续合约的限价委托
    # get_swap_limit_order_list()

    # # 永续合约持仓信息
    # list_swap_positions()
    #
    # 交易历史订单
    # print(order_algos_history())

    # print(get_order(insId='ETH-USDT-SWAP', ordId='2049135686594535424', clOrdId=''))

    # print(get_positions_history())

    # result = trade.place_algo_order(
    #     instId="ETH-USDT-SWAP",
    #     tdMode="isolated",
    #     side="buy",
    #     posSide="long",
    #     ordType="conditional",
    #     sz="10",
    #     slTriggerPx="4000",
    #     slOrdPx="-1",
    #     algoClOrdId="testAlgoPlaceOrder12080031",
    # )
    # print(result)

    # # 未完成的永续合约止盈止损委托
    # result = list_swap_unfinished_algo_order()
