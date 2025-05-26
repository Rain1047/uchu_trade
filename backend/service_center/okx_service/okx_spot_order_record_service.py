import logging

from backend._utils import SymbolFormatUtils
from backend.data_object_center.enum_obj import EnumTradeExecuteType, EnumOrdType, EnumSide
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord

from abc import ABC, abstractmethod
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class OrderProcessor(ABC):
    """订单处理基类"""

    @abstractmethod
    def process(self, order: Dict) -> bool:
        pass


class BuyOrderProcessor(OrderProcessor):
    """买入订单处理器"""

    def __init__(self, record_service):
        self.record_service = record_service

    def process(self, order: Dict) -> bool:
        # 检查订单是否存在
        current_order = SpotAlgoOrderRecord.get_by_ord_id(order.get('ordId'))

        if not current_order:
            # 新订单处理
            order['type'] = (EnumTradeExecuteType.LIMIT_ORDER.value
                             if order.get('ordType') == EnumOrdType.LIMIT.value
                             else EnumTradeExecuteType.MARKET_BUY.value)
            return self.record_service.save_or_update_limit_order_result(None, order)

        # 状态更新处理
        if current_order.get('status') != order.get('state'):
            return SpotAlgoOrderRecord.update_status_by_order(order)

        return True


class SellOrderProcessor(OrderProcessor):
    """卖出订单处理器"""

    def __init__(self, record_service):
        self.record_service = record_service

    def process(self, order: Dict) -> bool:
        # 设置订单类型
        order['type'] = (EnumTradeExecuteType.STOP_LOSS.value
                         if order.get('algoId')
                         else EnumTradeExecuteType.MARKET_SELL.value)

        if order.get('algoId'):
            return self._process_algo_order(order)
        return self._process_market_order(order)

    def _process_algo_order(self, order: Dict) -> bool:
        algo_order = SpotAlgoOrderRecord.get_by_algo_id(order.get('algoId'))
        if not algo_order:
            return self.record_service.save_or_update_stop_loss_result(None, order)

        if algo_order.get('status') != order.get('state'):
            return SpotAlgoOrderRecord.update_status_by_algo_order(order)

        return True

    def _process_market_order(self, order: Dict) -> bool:
        current_order = SpotAlgoOrderRecord.get_by_ord_id(order.get('ordId'))
        if not current_order:
            return self.record_service.save_or_update_stop_loss_result(None, order)

        if current_order.get('status') != order.get('state'):
            return SpotAlgoOrderRecord.update_status_by_order(order)

        return True


class OrderProcessorFactory:
    """订单处理器工厂"""

    def __init__(self, record_service):
        self.record_service = record_service

    def create_processor(self, side: str) -> Optional[OrderProcessor]:
        if side == EnumSide.BUY.value:
            return BuyOrderProcessor(self.record_service)
        elif side == EnumSide.SELL.value:
            return SellOrderProcessor(self.record_service)
        return None


# main service
class SpotOrderRecordService:
    """现货订单服务"""

    def __init__(self, trade_client, record_service):
        self.trade = trade_client
        self.processor_factory = OrderProcessorFactory(record_service)

    def save_update_spot_order_record(self):
        """保存更新现货订单记录"""
        # 获取历史订单
        history_orders = self._get_history_orders()
        if not history_orders:
            logger.info("No manual live spot orders.")
            return

        # 处理每个订单
        for order in history_orders:
            self._process_order(order)

    def _get_history_orders(self):
        """获取历史订单"""
        response = self.trade.get_orders_history_archive(
            instType="SPOT",
            ordType="limit,market"
        )

        if not (response and
                response.get('code') == '0' and
                response.get('data')):
            return []

        return response.get('data')

    def _process_order(self, order: Dict):
        """处理单个订单"""
        try:
            # 预处理订单数据
            order['ccy'] = SymbolFormatUtils.get_base_symbol(order.get('instId'))
            order['sz'] = order.get('accFillSz')
            order['px'] = order.get('avgPx')

            # 获取对应的处理器
            processor = self.processor_factory.create_processor(order.get('side'))
            if not processor:
                logger.error(f"Unknown order side: {order.get('side')}")
                return

            # 处理订单
            if not processor.process(order):
                logger.error(f"Failed to process order: {order.get('ordId')}")

        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
