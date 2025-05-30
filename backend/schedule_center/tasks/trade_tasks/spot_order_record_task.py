import logging

from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.enum_obj import EnumTdMode, EnumSide, EnumOrdType, EnumTradeExecuteType
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_order_service import OKXOrderService
from backend.service_center.okx_service.okx_ticker_service import OKXTickerService

logger = logging.getLogger(__name__)


class SpotOrderRecordService:
    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()
        self.okx_record_service = OKXOrderService()

    def save_update_spot_order_record(self):
        # [调用接口] 获取历史订单
        history_order_list = self.trade.get_orders_history_archive(
            instType="SPOT", ordType="limit,market"
        )
        if (history_order_list and history_order_list.get('code') == '0'
            and history_order_list.get('data')) and len(history_order_list.get('data')) > 0:
            history_order_list = history_order_list.get('data')
            for history_order in history_order_list:
                history_order['ccy'] = SymbolFormatUtils.get_base_symbol(history_order.get('instId'))
                # todo add column accFillSz and avgPx
                history_order['sz'] = history_order.get('accFillSz')
                history_order['px'] = history_order.get('avgPx')
                # 处理买入的订单
                if history_order.get('side') == EnumSide.BUY.value:
                    # 判断订单是否已存在
                    current_order = SpotAlgoOrderRecord.get_by_ord_id(history_order.get('ordId'))
                    # 如果不存在, 则新增并保存
                    if not current_order:
                        history_order['type'] = EnumTradeExecuteType.LIMIT_ORDER.value \
                            if history_order.get('ordType') == EnumOrdType.LIMIT.value \
                            else EnumTradeExecuteType.MARKET_BUY.value
                        self.okx_record_service.save_or_update_limit_order_result(None, history_order)
                    # 如果已经存在，则判状态是否改变，未改变则不修改
                    else:
                        if current_order.get('status') == history_order.get('state'):
                            continue
                        # 如果状态改变，则判断自动 or 手动
                        else:
                            SpotAlgoOrderRecord.update_status_by_order(history_order)
                elif history_order.get('side') == EnumSide.SELL.value:
                    history_order['type'] = EnumTradeExecuteType.STOP_LOSS.value \
                        if history_order.get('algoId') \
                        else EnumTradeExecuteType.MARKET_SELL.value
                    # 如果存在algoId，一定是根据止损委托创建的
                    if history_order.get('algoId'):
                        # 判断algo订单是否存在
                        algo_order = SpotAlgoOrderRecord.get_by_algo_id(history_order.get('algoId'))
                        # 当algo_order存在时
                        if algo_order:
                            if algo_order.get('status') == history_order.get('state'):
                                continue
                            else:
                                SpotAlgoOrderRecord.update_status_by_algo_order(history_order)
                        else:
                            self.okx_record_service.save_or_update_stop_loss_result(None, history_order)
                    # 如果不存在algoId，一定是根据市价委托创建的
                    else:
                        # 判断ord是否存在
                        current_order = SpotAlgoOrderRecord.get_by_ord_id(history_order.get('ordId'))
                        if not current_order:
                            self.okx_record_service.save_or_update_stop_loss_result(None, history_order)
                        else:
                            if current_order.get('status') == history_order.get('state'):
                                continue
                            else:
                                order = SpotAlgoOrderRecord.get_by_ord_id(history_order.get('ordId'))
                                if order:
                                    SpotAlgoOrderRecord.update_status_by_order(history_order)
                                else:
                                    self.okx_record_service.save_or_update_stop_loss_result(None, history_order)
                            SpotAlgoOrderRecord.update_status_by_order(history_order)

        else:
            logger.info("check_and_update_manual_live_order@no manual live spot orders.")


if __name__ == '__main__':
    sp = SpotOrderRecordService()
    # history = sp.trade.get_orders_history_archive(
    #     instType="SPOT", ordType="limit,market",
    #     instId="ETH-USDT"
    # )
    # print(history)
    sp.save_update_spot_order_record()
