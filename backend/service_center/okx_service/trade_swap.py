from logging import error
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

import pandas as pd

from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.object_center._object_dao.algo_order_record import AlgoOrderRecord
from backend.object_center._object_dao.attach_algo_orders_record import AttachAlgoOrdersRecord
from backend.object_center.enum_obj import (
    EnumAlgoOrdType,
    EnumTradeEnv,
    EnumTdMode,
    EnumOrdType, EnumState
)
from backend.strategy_center.strategy_result import StrategyExecuteResult
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend._utils import SymbolFormatUtils


class TradeSwapManager:
    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.okx = OKXAPIWrapper(env=EnumTradeEnv.MARKET.value)
        self.trade = self.okx.trade_api
        self.account = self.okx.account_api
        self.market = self.okx.market_api

    # def get_swap_limit_order_list(self) -> List[Dict[str, Any]]:
    #     swap_limit_orders = self.trade.get_order_list(
    #         instType='SWAP', ordType='limit')
    #     print(swap_limit_orders)
    #     return swap_limit_orders.get('data', []) if swap_limit_orders.get('code') == '0' else []

    def place_algo_order(self, st_result: StrategyExecuteResult) -> Dict[str, Any]:
        place_algo_order_result = self.trade.place_algo_order(
            instId="ETH-USDT",
            tdMode="cash",
            side="sell",
            ordType="conditional",
            sz="1",
            tpTriggerPx="",
            tpOrdPx="",
            slTriggerPx="2400",
            slOrdPx="2300",
            algoClOrdId="test_2024_12_07",
        )
        print(place_algo_order_result)
        return place_algo_order_result

    def amend_algo_order(
            self,
            instId: str,
            algoId: Optional[str] = '',
            algoClOrdId: Optional[str] = '',
            newSz: Optional[str] = '',
            newPx: Optional[str] = '',
            newSlTriggerPx: Optional[str] = '',
            newSlOrdPx: Optional[str] = ''
    ) -> Dict[str, Any]:
        return self.trade.amend_order(
            instId=instId,
            ordId=algoId,
            clOrdId=algoClOrdId,
            newSz=newSz,
            newPx=newPx,
            newSlTriggerPx=newSlTriggerPx,
            newSlOrdPx=newSlOrdPx
        )

    @staticmethod
    def find_order_by_attach_algo_id(data_dict: Dict[str, Any], target_attach_id: str) -> Optional[
        Dict[str, Any]]:
        if not data_dict.get('data') or not isinstance(data_dict['data'], list):
            return None

        return next(
            (order for order in data_dict['data']
             if order.get('algoClOrdId') == target_attach_id),
            None
        )


if __name__ == '__main__':
    # 1. 下单委托 place_order 市价入场 clOrdId
    # 合约市价下单

    trade_swap_manager = TradeSwapManager()
    # st_result = StrategyExecuteResult()
    # st_result.symbol = "ETH-USDT"
    # format_symbol = SymbolFormatUtils.get_swap_usdt(st_result.symbol)
    # st_result.symbol = format_symbol
    # st_result.side = "buy"
    # st_result.pos_side = "long"
    # st_result.sz = "1"
    # st_result.st_inst_id = 1
    # st_result.stop_loss_price = "3860"
    # st_result.signal = True
    # trade_result = trade_swap_manager.place_order(st_result)
    #
    # trade_swap_manager.save_place_algo_order_result(
    #     st_execute_result=st_result, place_order_result=trade_result)

    # ordId = result.get('data')[0].get('ordId')  # 后续查询成交明细时消费
    # print(result)

    # 2. 获取订单 get_order clOrdId -> 查看过程和结果
    # result = trade_swap_manager.get_order(instId='ETH-USDT-SWAP', ordId='2068880367670255616', clOrdId='')
    # print("通过ordId查看订单：")
    # print(result)

    # 3. 获取策略委托 get_algo_order algoClOrdId <- attachAlgoOrds-attachAlgoClOrdId
    # 委托订单待生效-live  委托订单已生效-effective
    result = trade_swap_manager.get_algo_order(algoId='', algoClOrdId='20241214223602ETH0001stInsId6174')
    attach_algo_orders = result['data']
    save_result = AttachAlgoOrdersRecord.save_or_update_attach_algo_orders(attach_algo_orders)
    print("通过algoClOrdId查看策略委托订单：")
    print(result)
    print(f"save_result:{save_result}")
    # 当get_algo_order by algoClOrdId 委托订单结果为effective时，遍历get_order，通过匹配algoClOrdId
    # 来获取订单结果的明细，判断订单的state是否为filled，如果是，则进行记录
    #
    # 4. 修改策略止损价
    # 只修改止损触发价，止盈传"", 取消止损，传"0"
    # result = trade_swap_manager.amend_algo_order(
    #     instId='ETH-USDT-SWAP', algoId='', algoClOrdId="attachAlgoClOrdId12082149",
    #     newSlTriggerPx='3994.5', newSlOrdPx='-1',
    # )
    # print(result)
    #
    # # 5. 匹配历史订单
    result = TradeSwapManager().trade.get_orders_history(instType="SWAP", instId='ETH-USDT-SWAP',
                                                         before='2052302587604230144')
    print("获取历史订单记录（近七天）, 查看ordId后的记录：")

    # orders_history_list = result.get('data')
    # 查找特定的 attachAlgoClOrdId
    target_attach_id = "attachAlgoClOrdId12082149"
    result = trade_swap_manager.find_order_by_attach_algo_id(result, target_attach_id)
    #
    if result:
        print(f"找到匹配的订单: {result}")
    else:
        print("未找到匹配的订单")

    print(result)
