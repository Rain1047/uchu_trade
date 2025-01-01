from backend.data_object_center.enum_obj import EnumSide
from backend.service_center.okx_service.record.buy_order_processor import BuyOrderProcessor
from backend.service_center.okx_service.record.order_processor import OrderProcessor
from backend.service_center.okx_service.record.sell_order_processor import SellOrderProcessor


class OrderProcessorFactory:
    @staticmethod
    def create_processor(order_side: str, record_service) -> OrderProcessor:
        if order_side == EnumSide.BUY.value:
            return BuyOrderProcessor(record_service)
        elif order_side == EnumSide.SELL.value:
            return SellOrderProcessor(record_service)
        raise ValueError(f"Unknown order side: {order_side}")