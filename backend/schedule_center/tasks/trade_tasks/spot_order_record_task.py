import logging
from datetime import datetime

from backend._decorators import singleton
from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.enum_obj import EnumTdMode, EnumSide, EnumOrdType, EnumTradeExecuteType, \
    EnumOrderState, EnumExecSource
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_ticker_service import OKXTickerService

logger = logging.getLogger(__name__)


class SpotOrderRecordTask:
    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()

    def save_update_spot_order_record(self):
        # [调用接口] 获取历史订单
        history_order_list = self.trade.get_orders_history_archive(
            instType="SPOT", ordType="limit"
        )
        if history_order_list and history_order_list.get('code') == '0':
            history_order_list = history_order_list.get('data')
            if len(history_order_list) > 0:
                for history_order in history_order_list:
                    # 处理买入的订单
                    if history_order.get('side') == EnumSide.BUY.value:
                        history_order['ccy'] = SymbolFormatUtils.get_base_symbol(history_order.get('instId'))
                        # todo add column accFillSz and avgPx
                        history_order['sz'] = history_order.get('accFillSz')
                        history_order['px'] = history_order.get('avgPx')
                        self.save_or_update_limit_order_result(config=None, result=history_order)

                    elif history_order.get('side') == EnumSide.SELL.value:
                        pass

        else:
            logger.info("check_and_update_manual_live_order@no manual live spot orders.")

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


if __name__ == '__main__':
    sp = SpotOrderRecordTask()
    history = sp.trade.get_orders_history_archive(
        instType="SPOT", ordType="limit,market",
        instId="ETH-USDT"
    )
    print(history)
