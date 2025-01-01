# 买入订单处理策略
from backend.data_object_center.enum_obj import EnumTradeExecuteType, EnumOrdType
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.service_center.okx_service.record.order_processor import OrderProcessor


class BuyOrderProcessor(OrderProcessor):
    def __init__(self, record_service):
        self.record_service = record_service

    def process(self, order: dict) -> bool:
        current_order = SpotAlgoOrderRecord.get_by_ord_id(order['ordId'])

        if not current_order:
            order['type'] = (EnumTradeExecuteType.LIMIT_ORDER.value
                             if order['ordType'] == EnumOrdType.LIMIT.value
                             else EnumTradeExecuteType.MARKET_BUY.value)
            return self.record_service.save_or_update_limit_order_result(None, order)
        elif current_order.get('status') != order['state']:
            return SpotAlgoOrderRecord.update_status_by_order(order)
        return True
