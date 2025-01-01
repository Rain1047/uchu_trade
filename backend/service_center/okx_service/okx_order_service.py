from backend._utils import SymbolFormatUtils
from backend.data_object_center.enum_obj import EnumTradeExecuteType, EnumExecSource, EnumAlgoOrderState, \
    EnumAlgoOrdType
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord


class OKXOrderService:
    @staticmethod
    def save_or_update_limit_order_result(config: dict | None, result: dict):
        if result.get('ordType') == EnumAlgoOrdType.CONDITIONAL.value:
            result['px'] = result.get('slTriggerPx', '0')

        print(f"insert result is {result}")
        stop_loss_data = {
            'ccy': result.get('ccy') if result.get('ccy') else SymbolFormatUtils.get_base_symbol(result.get('instId')),
            'type': result.get('type'),
            'config_id': config.get('id') if config else '',
            'sz': result.get('sz'),
            'amount': config.get('amount') if config else
            str(float(result.get('sz')) * float(result.get('px'))),
            'target_price': config.get('target_price', '') if config else result.get('px', ''),
            'exec_price': result.get('avgPx'),
            'ordId': result.get('ordId'),
            'algoId': result.get('algoId'),
            'status': result.get('state'),
            'exec_source': EnumExecSource.AUTO.value if config else EnumExecSource.MANUAL.value,
            'uTime': result.get('uTime'),
            'cTime': result.get('cTime')
        }
        success = SpotAlgoOrderRecord.insert_or_update(stop_loss_data)
        print(f"Insert limit order: {'success' if success else 'failed'}")

    @staticmethod
    def save_or_update_stop_loss_result(config: dict | None, result: dict):
        print(result)
        stop_loss_data = {
            'ccy': config.get('ccy') if config else
            SymbolFormatUtils.get_base_symbol(result.get('instId')),
            'type': result.get('type'),
            'config_id': config.get('id') if config else '',
            'sz': config.get('sz') if config else result.get('sz'),
            'amount': config.get('amount') if config else
            str(float(result.get('sz', '0')) * float(result.get('px', '0'))),
            'target_price': config.get('target_price') if config else
            result.get('px'),
            'exec_price': result.get('avgPx'),
            'ordId': result.get('ordId'),
            'algoId': result.get('algoId'),
            'status': result.get('state'),
            'exec_source': EnumExecSource.AUTO.value if config else EnumExecSource.MANUAL.value,
            'uTime': result.get('uTime'),
            'cTime': result.get('cTime')
        }
        success = SpotAlgoOrderRecord.insert_or_update(stop_loss_data)
        print(f"Insert stop loss: {'success' if success else 'failed'}")
