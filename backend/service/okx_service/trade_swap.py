import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.enum_obj import EnumAlgoOrdType, EnumTradeEnv, EnumTdMode, EnumOrdType
from backend.data_center.data_object.res.strategy_execute_result import StrategyExecuteResult
from backend.data_center.kline_data.kline_data_reader import KlineDataReader

kline_reader = KlineDataReader()
okx = OKXAPIWrapper(env=EnumTradeEnv.MARKET.value)
trade = okx.trade_api
account = okx.account_api
market = okx.market_api


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


def find_order_by_attach_algo_id(data_dict, target_attach_id):
    # 确保有 data 字段且是列表
    if not data_dict.get('data') or not isinstance(data_dict['data'], list):
        return None

    # 遍历 data 列表查找匹配的字典
    for order in data_dict['data']:
        if order.get('algoClOrdId') == target_attach_id:
            return order

    return None


if __name__ == '__main__':
    # 1. 下单委托 place_order 市价入场 clOrdId
    # 合约市价下单
    current_time = datetime.now().strftime("%H%M")
    attachAlgoClOrdId = f"attachAlgoClOrdId1208{current_time}"
    clOrdId = f"clOrdId1208{current_time}"

    # attachAlgoClOrdId = "attachAlgoClOrdId12082142"
    # clOrdId = "clOrdId12082142"
    print(f"clOrdId: {clOrdId}, attachAlgoClOrdId: {attachAlgoClOrdId}")
    # # last_price = market.get_ticker(instId=instId)['data'][0]['last']

    # attachAlgoOrds = [
    #     {
    #         'attachAlgoClOrdId': attachAlgoClOrdId,  # 需要唯一
    #         'slTriggerPx': "3995",
    #         'slOrdPx': "-1",
    #         'tpTriggerPx': "4005",
    #         'tpOrdPx': "-1"
    #     }
    # ]
    #
    # result = trade.place_order(
    #     instId="ETH-USDT-SWAP",
    #     tdMode="isolated",
    #     side="buy",
    #     posSide="long",
    #     ordType="market",
    #     sz="1",  # 委托数量
    #     clOrdId=clOrdId,
    #     attachAlgoOrds=attachAlgoOrds
    # )
    # ordId = result.get('data')[0].get('ordId')  # 后续查询成交明细时消费
    # print(f"ordId: {ordId}")  #
    # print(result)
    # #
    # # 2. 获取订单 get_order clOrdId -> 查看过程和结果
    # result = trade.get_order(instId='ETH-USDT-SWAP', ordId='', clOrdId=clOrdId)
    # print("通过clOrdId查看订单：")
    # print(result)
    # #
    # # # 3. 获取策略委托 get_algo_order algoClOrdId <- attachAlgoOrds-attachAlgoClOrdId
    # # 委托订单待生效-live  委托订单已生效-effective
    # result = trade.get_algo_order(algoId='', algoClOrdId=attachAlgoClOrdId)
    # print("通过algoClOrdId查看策略委托订单：")
    # print(result)
    # 当get_algo_order by algoClOrdId 委托订单结果为effective时，遍历get_order，通过匹配algoClOrdId
    # 来获取订单结果的明细，判断订单的state是否为filled，如果是，则进行记录

    # 4. 修改策略止损价
    # 只修改止损触发价，止盈传"", 取消止损，传"0"
    # result = trade.amend_algo_order(
    #     instId='ETH-USDT-SWAP', algoId='', algoClOrdId="attachAlgoClOrdId12082149",
    #     newSlTriggerPx='3994.5', newSlOrdPx='-1',
    #     newTpTriggerPx="", newTpOrdPx="",
    # )
    # print(result)

    # 5. 匹配历史订单
    result = trade.get_orders_history(instType="SWAP", instId='ETH-USDT-SWAP', before='2052302587604230144')
    print("获取历史订单记录（近七天）, 查看ordId后的记录：")

    orders_history_list = result.get('data')
    # 查找特定的 attachAlgoClOrdId
    target_attach_id = "attachAlgoClOrdId12082149"
    result = find_order_by_attach_algo_id(result, target_attach_id)

    if result:
        print(f"找到匹配的订单: {result}")
    else:
        print("未找到匹配的订单")

    print(result)
