import logging

from backend._utils import SymbolFormatUtils, LogConfig
from backend.data_object_center.enum_obj import EnumTradeExecuteType, EnumOrdType, EnumSide
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord

from abc import ABC, abstractmethod
from typing import Optional, Dict

logger = LogConfig.get_logger(__name__)


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
        logger.info("初始化SpotOrderRecordService")

    def save_update_spot_order_record(self):
        """保存更新现货订单记录"""
        # 获取历史订单
        history_orders = self._get_history_orders()
        if not history_orders:
            logger.info("No manual live spot orders.")
            return

        logger.info(f"获取到 {len(history_orders)} 条历史订单记录")
        # 处理每个订单
        for order in history_orders:
            self._process_order(order)

    def _get_history_orders(self):
        """获取历史订单"""
        logger.info("开始获取历史订单")
        response = self.trade.get_orders_history_archive(
            instType="SPOT",
            ordType="limit,market"
        )

        if not (response and
                response.get('code') == '0' and
                response.get('data')):
            logger.warning("获取历史订单失败或没有数据")
            return []

        logger.info(f"成功获取历史订单，数量: {len(response.get('data'))}")
        return response.get('data')

    def _process_order(self, order: Dict):
        """处理单个订单"""
        try:
            # 预处理订单数据
            order['ccy'] = SymbolFormatUtils.get_base_symbol(order.get('instId'))
            
            # 处理数量和价格
            if order.get('fillSz'):  # 优先使用fillSz
                order['sz'] = order.get('fillSz')
            elif order.get('sz'):  # 其次使用sz
                order['sz'] = order.get('sz')
            else:
                order['sz'] = '0'
                
            if order.get('fillPx'):  # 优先使用fillPx
                order['px'] = order.get('fillPx')
            elif order.get('avgPx'):  # 其次使用avgPx
                order['px'] = order.get('avgPx')
            elif order.get('px'):  # 再次使用px
                order['px'] = order.get('px')
            else:
                order['px'] = '0'
                
            # 计算amount（如果为空）
            if not order.get('amount'):
                try:
                    amount = float(order['sz']) * float(order['px'])
                    order['amount'] = str(amount)
                except (ValueError, TypeError):
                    order['amount'] = '0'

            # 处理目标价格
            if order.get('tpTriggerPx'):  # 优先使用tpTriggerPx
                order['target_price'] = order.get('tpTriggerPx')
            elif order.get('target_price'):  # 其次使用target_price
                order['target_price'] = order.get('target_price')
            else:
                order['target_price'] = order['px']  # 如果没有目标价格，使用当前价格

            # 处理执行价格
            if order.get('fillPx'):  # 优先使用fillPx
                order['exec_price'] = order.get('fillPx')
            elif order.get('avgPx'):  # 其次使用avgPx
                order['exec_price'] = order.get('avgPx')
            elif order.get('px'):  # 再次使用px
                order['exec_price'] = order.get('px')
            else:
                order['exec_price'] = '0'

            logger.info(f"处理订单数据: sz={order['sz']}, px={order['px']}, amount={order.get('amount')}, "
                       f"target_price={order.get('target_price')}, exec_price={order.get('exec_price')}")

            # 获取对应的处理器
            processor = self.processor_factory.create_processor(order.get('side'))
            if not processor:
                logger.error(f"未知的订单方向: {order.get('side')}")
                return

            # 处理订单
            if not processor.process(order):
                logger.error(f"处理订单失败: {order.get('ordId')}")
            else:
                logger.info(f"成功处理订单: {order.get('ordId')}")

        except Exception as e:
            logger.error(f"处理订单时发生错误: {str(e)}", exc_info=True)
