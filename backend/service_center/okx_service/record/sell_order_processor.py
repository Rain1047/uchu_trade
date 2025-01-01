# 卖出订单处理策略
from backend.data_object_center.enum_obj import EnumTradeExecuteType
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.service_center.okx_service.record.order_processor import OrderProcessor


class SellOrderProcessor(OrderProcessor):
    def __init__(self, record_service):
        self.record_service = record_service

    def process(self, order: dict) -> bool:
        order['type'] = (EnumTradeExecuteType.STOP_LOSS.value
                         if order.get('algoId')
                         else EnumTradeExecuteType.MARKET_SELL.value)

        if order.get('algoId'):
            return self._process_algo_order(order)
        return self._process_market_order(order)

    def _process_algo_order(self, order):
        algo_order = SpotAlgoOrderRecord.get_by_algo_id(order['algoId'])
        if algo_order and algo_order.get('status') != order['state']:
            return SpotAlgoOrderRecord.update_status_by_algo_order(order)
        return self.record_service.save_or_update_stop_loss_result(None, order)

    def _process_market_order(self, order):
        current_order = SpotAlgoOrderRecord.get_by_ord_id(order['ordId'])
        if not current_order:
            return self.record_service.save_or_update_stop_loss_result(None, order)
        if current_order.get('status') != order['state']:
            return SpotAlgoOrderRecord.update_status_by_order(order)
        return True

