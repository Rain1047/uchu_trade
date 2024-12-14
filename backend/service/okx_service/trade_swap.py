from logging import error
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.data_object.enum_obj import (
    EnumAlgoOrdType,
    EnumTradeEnv,
    EnumTdMode,
    EnumOrdType, EnumState
)
from backend.data_center.data_object.res.strategy_execute_result import StrategyExecuteResult
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.object_center.object_dao.algo_order_record import AlgoOrderRecord
from backend.object_center.object_dao.attach_algo_orders_record import AttachAlgoOrdersRecord
from backend.utils.utils import SymbolFormatUtils


class TradeSwapManager:
    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.okx = OKXAPIWrapper(env=EnumTradeEnv.MARKET.value)
        self.trade = self.okx.trade_api
        self.account = self.okx.account_api
        self.market = self.okx.market_api

    def cancel_swap_unfinished_algo_order(self, swap_unfinished_algo_list: List[Dict[str, Any]]) -> None:
        cancel_algo_list = [
            {
                'instId': algo_order.get('instId'),
                'algoId': algo_order.get('algoId')
            }
            for algo_order in swap_unfinished_algo_list
        ]
        self.trade.cancel_algo_order(cancel_algo_list)

    def get_swap_limit_order_list(self) -> List[Dict[str, Any]]:
        swap_limit_orders = self.trade.get_order_list(
            instType='SWAP', ordType='limit')
        print(swap_limit_orders)
        return swap_limit_orders.get('data', []) if swap_limit_orders.get('code') == '0' else []

    def list_swap_unfinished_algo_order(self) -> List[Dict[str, Any]]:
        try:
            swap_algo_orders = self.trade.order_algos_list(
                instType='SWAP',
                ordType=EnumAlgoOrdType.CONDITIONAL_OCO.value
            )
            print(swap_algo_orders)

            data = swap_algo_orders.get('data')
            if swap_algo_orders.get('code') == '0' and data and isinstance(data, list):
                return data
            return []
        except Exception as e:
            error(f"获取算法订单列表失败: {str(e)}")
            return []

    @staticmethod
    def get_attach_algo_cl_ordId(st_result: StrategyExecuteResult) -> str:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        return (
                current_time +
                st_result.symbol.split('-')[0] +
                # 使用 zfill 方法将数字字符串填充为4位
                str(st_result.st_inst_id).zfill(4) + "stInsId" +
                str(uuid.uuid4())[:4])

    def place_order(self, st_result: StrategyExecuteResult) -> Dict[str, Any]:

        attach_algo_cl_ordId = self.get_attach_algo_cl_ordId(st_result)
        print("place_order@attach_algo_cl_ordId: " + attach_algo_cl_ordId)
        attachAlgoOrds = [
            {
                'attachAlgoClOrdId': attach_algo_cl_ordId,
                'slTriggerPx': st_result.stop_loss_price,
                'slOrdPx': "-1",
            }
        ]
        format_symbol = SymbolFormatUtils.get_swap_usdt(st_result.symbol)
        place_order_result = self.trade.place_order(
            instId=format_symbol,
            tdMode=EnumTdMode.ISOLATED.value,
            side=st_result.side,
            posSide=st_result.pos_side,
            ordType=EnumOrdType.MARKET.value,
            sz=st_result.sz,
            attachAlgoOrds=attachAlgoOrds,
        )

        place_order_result['attachAlgoClOrdId'] = attach_algo_cl_ordId
        place_order_result['symbol'] = format_symbol
        print(place_order_result)
        return place_order_result

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

    def order_algos_history(self) -> Dict[str, Any]:
        return self.trade.order_algos_history(
            orderType=EnumAlgoOrdType.CONDITIONAL_OCO.value,
            instType='SWAP',
            state='canceled'
        )

    def get_order(self, instId: str, ordId: Optional[str], clOrdId: Optional[str]) -> Dict[str, Any]:
        return self.trade.get_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    def get_algo_order(self, algoId: Optional[str] = '', algoClOrdId: Optional[str] = ''):
        return self.trade.get_algo_order(algoId=algoId, algoClOrdId=algoClOrdId)

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

    def get_orders_history(self, instType: Optional[str], instId: Optional[str], before: Optional[str]):
        return self.trade.get_orders_history(instType=instType, instId=instId, before=before)


def _save_trade_result(st_execute_result: 'StrategyExecuteResult', place_order_result: dict):
    try:
        algo_order_record = AlgoOrderRecord()

        # 从返回结果中提取第一个订单数据（data[0]）
        post_order_data = place_order_result['data'][0]
        algo_order_record.cl_ord_id = post_order_data['clOrdId']
        algo_order_record.ord_id = post_order_data['ordId']
        algo_order_record.s_code = post_order_data['sCode']
        algo_order_record.s_msg = post_order_data['sMsg']
        algo_order_record.ts = post_order_data['ts']

        algo_order_record.tag = post_order_data['tag']
        algo_order_record.attach_algo_cl_ord_id = place_order_result['attachAlgoClOrdId']

        # 封装StrategyExecuteResult
        algo_order_record.symbol = place_order_result['symbol']
        algo_order_record.side = st_execute_result.side
        algo_order_record.pos_side = st_execute_result.pos_side
        algo_order_record.sz = st_execute_result.sz
        algo_order_record.st_inst_id = st_execute_result.st_inst_id
        algo_order_record.interval = st_execute_result.interval

        # 订单结果参数
        # 调用get_order方法
        get_order_result = TradeSwapManager().get_order(
            instId=algo_order_record.symbol,
            ordId=algo_order_record.ord_id,
            clOrdId=algo_order_record.cl_ord_id
        )
        get_order_data = get_order_result['data'][0]
        print(get_order_data)

        algo_order_record.fill_px = get_order_data['fillPx']
        algo_order_record.fill_sz = get_order_data['fillSz']
        algo_order_record.avg_px = get_order_data['avgPx']
        algo_order_record.pnl = '0'
        algo_order_record.state = EnumState.LIVE.value
        algo_order_record.lever = '5'
        algo_order_record.create_time = datetime.now()
        algo_order_record.ord_id = datetime.now()
        attach_algo_orders = get_order_result['data'][0].get('attachAlgoOrds', [])
        AttachAlgoOrdersRecord.save_attach_algo_orders_from_response(attach_algo_orders)
        AlgoOrderRecord.insert(algo_order_record.to_dict())
    except Exception as e:
        print(f"process_strategy@e_handle_trade_result error: {e}")


if __name__ == '__main__':
    # 1. 下单委托 place_order 市价入场 clOrdId
    # 合约市价下单

    trade_swap_manager = TradeSwapManager()
    # # current_time = datetime.now().strftime("%H%M")
    # # attachAlgoClOrdId = f"attachAlgoClOrdId1208{current_time}"
    # # clOrdId = f"clOrdId1208{current_time}"
    # #
    # st_result = StrategyExecuteResult()
    # st_result.symbol = "ETH-USDT"
    # st_result.side = "buy"
    # st_result.pos_side = "long"
    # st_result.sz = "1"
    # st_result.st_inst_id = 1
    # st_result.stop_loss_price = "3850"
    # st_result.signal = True
    #
    # # # last_price = market.get_ticker(instId=instId)['data'][0]['last']
    #
    # result = trade_swap_manager.place_order(st_result)
    # _save_trade_result(st_result, result)

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
    save_result = AttachAlgoOrdersRecord.save_attach_algo_orders_from_response(attach_algo_orders)
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
    # result = trade_swap_manager.get_orders_history(instType="SWAP", instId='ETH-USDT-SWAP',
    #                                                before='2052302587604230144')
    # print("获取历史订单记录（近七天）, 查看ordId后的记录：")
    #
    # orders_history_list = result.get('data')
    # # 查找特定的 attachAlgoClOrdId
    # target_attach_id = "attachAlgoClOrdId12082149"
    # result = trade_swap_manager.find_order_by_attach_algo_id(result, target_attach_id)
    #
    # if result:
    #     print(f"找到匹配的订单: {result}")
    # else:
    #     print("未找到匹配的订单")
    #
    # print(result)
