from backend.data_object_center.enum_obj import EnumTradeExecuteType, EnumExecSource
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord


class OKXOrderService:
    @staticmethod
    def save_or_update_limit_order_result(config: dict | None, result: dict):
        stop_loss_data = {
            'ccy': result.get('ccy'),
            'type': EnumTradeExecuteType.LIMIT_ORDER.value if config else EnumTradeExecuteType.MARKET_BUY.value,
            'config_id': config.get('id') if config else '',
            'sz': result.get('sz'),
            'amount': config.get('amount') if config else
            str(float(result.get('sz')) * float(result.get('px'))),
            'target_price': config.get('target_price') if config else result.get('px'),
            'ordId': result.get('ordId'),
            'status': result.get('state'),
            'exec_source': EnumExecSource.AUTO.value if config else EnumExecSource.MANUAL.value,
            'uTime': result.get('uTime'),
            'cTime': result.get('cTime')
        }
        success = SpotAlgoOrderRecord.insert_or_update(stop_loss_data)
        print(f"Insert limit order: {'success' if success else 'failed'}")
