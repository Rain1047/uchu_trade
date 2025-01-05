from backend.controller_center.balance.balance_request import TradeRecordPageRequest
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord


class RecordService:

    @staticmethod
    def list_config_execute_records(config_execute_history_request: TradeRecordPageRequest):
        return SpotAlgoOrderRecord.list_spot_algo_order_record_by_conditions(config_execute_history_request)
