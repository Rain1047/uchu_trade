import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from backend._decorators import add_docstring
from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.object_center._object_dao.swap_algo_order_record import SwapAlgoOrderRecord
from backend.object_center._object_dao.swap_attach_algo_orders_record import SwapAttachAlgoOrdersRecord
from backend.object_center.enum_obj import EnumAlgoOrdType, EnumTdMode, EnumOrdType
from backend.strategy_center.strategy_result import StrategyExecuteResult

logger = logging.getLogger(__name__)


class OKXAlgoOrderService:

    def __init__(self):
        self.okx = OKXAPIWrapper()
        self.trade = self.okx.trade_api
        self.funding = self.okx.funding_api
        self.account = self.okx.account

    # [主要方法] 取消所有未成交的现货限价单
    @add_docstring("[主要方法] 取消所有未成交的现货限价单")
    def cancel_all_spot_algo_orders(self):
        spot_unfinished_algo_list = self.list_spot_unfinished_algo_order()
        cancel_algo_list = []
        for algo_order in spot_unfinished_algo_list:
            cancel_algo_list.append(
                {
                    'instId': algo_order.get('instId'),
                    'algoId': algo_order.get('algoId')
                }
            )
        self.cancel_spot_unfinished_algo_order(cancel_algo_list)

    # [主要方法] 取消所有未成交的合约限价单
    @add_docstring("[主要方法] 取消所有未成交的现货限价单")
    def cancel_all_swap_algo_orders(self):
        spot_unfinished_algo_list = self.list_swap_unfinished_algo_order()
        cancel_algo_list = []
        for algo_order in spot_unfinished_algo_list:
            cancel_algo_list.append(
                {
                    'instId': algo_order.get('instId'),
                    'algoId': algo_order.get('algoId')
                }
            )
        self.cancel_swap_unfinished_algo_order(cancel_algo_list)

    @add_docstring("[主要方法] 根据策略执行结果市价下单")
    def place_order_by_st_result(self, st_result: StrategyExecuteResult) -> Dict[str, Any]:

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

    # 获取现货所有未完成的止盈止损委托
    @add_docstring("获取现货所有未完成的止盈止损委托")
    def list_spot_unfinished_algo_order(self) -> List[Dict[str, Any]]:
        """
        获取未完成的现货算法订单列表

        Returns:
            List[Dict[str, Any]]: 订单列表，如果没有订单或发生错误则返回空列表
        """
        try:
            result = self.trade.order_algos_list(
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
    @add_docstring("取消现货所有未完成的止盈止损和限价委托")
    def cancel_spot_unfinished_algo_order(self, algo_orders):
        cancel_result = self.trade.cancel_algo_order(algo_orders)
        print(cancel_result)

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
            print(f"获取算法订单列表失败: {str(e)}")
            return []

    def cancel_swap_unfinished_algo_order(self, swap_unfinished_algo_list: List[Dict[str, Any]]) -> None:
        cancel_algo_list = [
            {
                'instId': algo_order.get('instId'),
                'algoId': algo_order.get('algoId')
            }
            for algo_order in swap_unfinished_algo_list
        ]
        self.trade.cancel_algo_order(cancel_algo_list)

    @staticmethod
    def get_attach_algo_cl_ordId(st_result: StrategyExecuteResult) -> str:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        return (
                current_time +
                st_result.symbol.split('-')[0] +
                # 使用 zfill 方法将数字字符串填充为4位
                str(st_result.st_inst_id).zfill(4) + "stInsId" +
                str(uuid.uuid4())[:4])

    def save_execute_algo_order_result(self, st_execute_result: 'StrategyExecuteResult', place_order_result: dict) \
            -> bool:
        try:
            algo_order_record = SwapAlgoOrderRecord()
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
            if st_execute_result is not None:
                algo_order_record.side = st_execute_result.side
                algo_order_record.pos_side = st_execute_result.pos_side
                algo_order_record.sz = st_execute_result.sz
                algo_order_record.st_inst_id = st_execute_result.st_inst_id
                algo_order_record.interval = st_execute_result.interval

            # 订单结果参数，调用get_order方法
            get_order_result = self.trade.get_order(
                instId=algo_order_record.symbol,
                ordId=algo_order_record.ord_id,
                clOrdId=algo_order_record.cl_ord_id
            )
            get_order_data = get_order_result['data'][0]
            algo_order_record.fill_px = get_order_data['fillPx']
            algo_order_record.fill_sz = get_order_data['fillSz']
            algo_order_record.avg_px = get_order_data['avgPx']
            algo_order_record.pnl = get_order_data['pnl']
            algo_order_record.state = get_order_data['state']
            algo_order_record.lever = get_order_data['lever']
            algo_order_record.source = get_order_data['source']
            algo_order_record.create_time = datetime.now()
            algo_order_record.update_time = datetime.now()
            SwapAlgoOrderRecord.save_or_update_algo_order_record(algo_order_record.to_dict())

            # 委托止盈止损，调用get_algo_order方法
            attach_algo_order_result = self.trade.get_algo_order(algoId='', algoClOrdId=place_order_result[
                'attachAlgoClOrdId'])
            attach_algo_orders = attach_algo_order_result['data']
            SwapAttachAlgoOrdersRecord.save_or_update_attach_algo_orders(attach_algo_orders)
            return True
        except Exception as e:
            print(f"process_strategy@e_handle_trade_result error: {e}")
            return False

    def save_modified_algo_order(self, source_algo_order_record: 'SwapAlgoOrderRecord', latest_order_data: dict) -> bool:
        try:
            algo_order_record = SwapAlgoOrderRecord()
            algo_order_record.cl_ord_id = latest_order_data['clOrdId']
            algo_order_record.ord_id = latest_order_data['ordId']
            algo_order_record.tag = latest_order_data['tag']
            algo_order_record.attach_algo_cl_ord_id = latest_order_data['attachAlgoClOrdId']
            algo_order_record.fill_px = latest_order_data['fillPx']
            algo_order_record.fill_sz = latest_order_data['fillSz']
            algo_order_record.avg_px = latest_order_data['avgPx']
            algo_order_record.pnl = latest_order_data['pnl']
            algo_order_record.state = latest_order_data['state']
            algo_order_record.lever = latest_order_data['lever']
            algo_order_record.source = latest_order_data['source']
            algo_order_record.create_time = datetime.now()
            algo_order_record.update_time = datetime.now()

            algo_order_record.attach_algo_cl_ord_id = source_algo_order_record.attach_algo_cl_ord_id
            algo_order_record.symbol = source_algo_order_record.symbol
            algo_order_record.pos_side = source_algo_order_record.pos_side
            algo_order_record.side = source_algo_order_record.side
            algo_order_record.sz = float(source_algo_order_record.sz)
            algo_order_record.st_inst_id = int(source_algo_order_record.st_inst_id)
            algo_order_record.interval = source_algo_order_record.interval
            SwapAlgoOrderRecord.save_or_update_algo_order_record(algo_order_record.to_dict())
            return True
        except Exception as e:
            print(f"process_strategy@e_handle_trade_result error: {e}")
            return False
