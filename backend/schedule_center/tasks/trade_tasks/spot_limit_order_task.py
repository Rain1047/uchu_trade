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


@singleton
class SpotLimitOrderTask:

    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()

    # [限价委托主任务] 检查并更新自动限价委托
    def check_and_update_auto_live_order(self):
        # 1. get all unfinished orders
        live_order_list = SpotAlgoOrderRecord.list_live_auto_spot_orders()
        if len(live_order_list) > 0:
            for live_order in live_order_list:
                ordId = live_order.get('ordId')
                # 2. check order status
                latest_order_result = self.trade.get_order(instId=SymbolFormatUtils.get_usdt(live_order.get('ccy')),
                                                           ordId=ordId)
                print(latest_order_result)
                if latest_order_result and latest_order_result.get('code') == '0':
                    latest_order = latest_order_result.get('data')[0]
                    print(f"ordId:{latest_order.get('ordId')} latest status is {latest_order.get('state')}.")
                    if latest_order.get('state') == EnumOrderState.CANCELED.value:
                        SpotAlgoOrderRecord.update_status_by_ord_id(ordId, EnumOrderState.CANCELED.value)
                    if latest_order.get('state') == EnumOrderState.FILLED.value:
                        SpotAlgoOrderRecord.update_status_by_ord_id(ordId, EnumOrderState.FILLED.value)
                    elif latest_order.get('state') == EnumOrderState.LIVE.value:
                        logger.info(f"check_and_update_auto_spot_live_order@ {latest_order} is live")
                        spot_trade_config = SpotTradeConfig.get_effective_spot_config_by_id(live_order.get('config_id'))
                        if spot_trade_config:
                            self.update_limit_order(spot_trade_config, latest_order)
                    else:
                        logger.info(
                            f"check_and_update_auto_spot_live_order@ {latest_order} is {latest_order.get('state')}.")
        else:
            logger.info("check_and_update_auto_spot_live_order@no auto live spot orders.")

    def process_new_auto_limit_order_task(self):
        limit_order_configs = SpotTradeConfig().get_effective_and_unfinished_limit_order_configs()
        if len(limit_order_configs) > 0:
            for config in limit_order_configs:
                print(config)
                self.execute_limit_order_task(config)

    # [限价委托方法] 更新生效中的限价委托
    def update_limit_order(self, spot_trade_config: dict, latest_order: dict):
        target_price = spot_trade_config.get('target_price')
        if not target_price:
            target_price = (self.okx_ticker_service.get_target_indicator_latest_price_by_spot_config(
                config=spot_trade_config))
        amount = spot_trade_config.get('amount')
        if not amount:
            # 获取真实的账户余额 赎回赚币-划转到交易账户
            real_account_balance = self.okx_balance_service.get_real_account_balance(ccy="USDT")
            pct = spot_trade_config.get('percentage')
            amount = str(round(float(real_account_balance) * float(pct) / 100, 6))
        sz = str(round(float(amount) / float(target_price), 6))

        self.trade.amend_order(
            instId=SymbolFormatUtils.get_usdt(spot_trade_config.get('ccy')),
            ordId=latest_order.get('ordId'),
            newPx=target_price,
            newSz=sz
        )

    # [调度子任务] 根据配置进行限价委托
    def execute_limit_order_task(self, config: dict):

        ccy = config.get('ccy')
        target_price = config.get('target_price')
        if not target_price:
            target_price = self.okx_ticker_service.get_target_indicator_latest_price_by_spot_config(
                config=config
            )

        target_amount = config.get('amount')
        if not target_amount:
            # 获取真实的账户余额 赎回赚币-划转到交易账户
            real_account_balance = self.okx_balance_service.get_real_account_balance(ccy="USDT")
            pct = config.get('percentage')
            target_amount = str(round(float(real_account_balance) * float(pct) / 100, 6))
        sz = str(round(float(target_amount) / float(target_price), 6))
        config['sz'] = sz
        config['amount'] = str(target_amount)
        config['target_price'] = str(target_price)
        print(f"target amount: {target_amount}, target price: {target_price}, sz:{sz}")
        result = self.trade.place_order(
            instId=SymbolFormatUtils.get_usdt(ccy),
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.BUY.value,
            ordType=EnumOrdType.LIMIT.value,
            sz=sz,
            px=target_price
        )
        if result and result.get('code') == '0':
            result = result.get('data')[0]
            self.save_or_update_limit_order_result(config, result, exec_source=EnumExecSource.AUTO.value)
        SpotTradeConfig.minus_exec_nums(config)
        print(result)

    @staticmethod
    def save_or_update_limit_order_result(config: dict, result: dict, exec_source: str):

        # 转换时间戳为datetime对象 (timestamp是毫秒)
        c_time = result.get('cTime')
        u_time = result.get('uTime')
        print(c_time)

        stop_loss_data = {
            'ccy': config.get('ccy') if exec_source == EnumExecSource.AUTO.value
            else SymbolFormatUtils.get_base_symbol(result.get('instId')),
            'type': EnumTradeExecuteType.LIMIT_ORDER.value,
            'config_id': config.get('id') if exec_source == EnumExecSource.AUTO.value else '',
            'sz': config.get('sz') if exec_source == EnumExecSource.AUTO.value else
            result.get('sz'),
            'amount': config.get('amount') if exec_source == EnumExecSource.AUTO.value else
            float(result.get('sz')) * float(result.get('px')),
            'target_price': config.get('target_price') if exec_source == EnumExecSource.AUTO.value else
            result.get('px'),
            'ordId': result.get('ordId'),
            'status': result.get('state'),
            'exec_source': exec_source,
            'uTime': u_time,
            'cTime': c_time
        }
        success = SpotAlgoOrderRecord.insert_or_update(stop_loss_data)
        print(f"Insert limit order: {'success' if success else 'failed'}")

    def update_limit_order_status(self):
        live_order_list = SpotAlgoOrderRecord.list_by_status(EnumOrderState.LIVE.value)
        if len(live_order_list) > 1:
            for live_order in live_order_list:
                latest_order = self.trade.get_order(instId=SymbolFormatUtils.get_usdt(live_order.get('ccy')),
                                                    ordId=live_order.get('ordId'))
                latest_status = latest_order.get('data')[0].get('state')
                if latest_order.get('data')[0].get('state') != EnumOrderState.LIVE.value:
                    SpotAlgoOrderRecord.update_status_by_ord_id(live_order.get('ordId'), latest_status)

    def check_and_update_manual_live_order(self):
        # [查看数据库] 获取所有未完成的订单，更新其状态
        manual_live_order_list = SpotAlgoOrderRecord.list_live_manual_spot_orders()
        if len(manual_live_order_list) > 0:
            for manual_live_order in manual_live_order_list:
                latest_order = self.trade.get_order(instId=SymbolFormatUtils.get_usdt(manual_live_order.get('ccy')),
                                                    ordId=manual_live_order.get('ordId'))
                if latest_order and latest_order.get('code') == '0':
                    if latest_order.get('data')[0].get('state') != EnumOrderState.LIVE.value:
                        SpotAlgoOrderRecord.update_status_by_ord_id(manual_live_order.get('ordId'),
                                                                    latest_order.get('data')[0].get('state'))
        # [调用接口] 获取所有未完成的订单
        order_list_result = self.trade.get_order_list(
            instType="SPOT", state=EnumOrderState.LIVE.value, ordType="market,limit")
        if order_list_result and order_list_result.get('code') == '0':
            order_list = order_list_result.get('data')
            if len(order_list) > 0:
                for order in order_list:
                    self.save_or_update_limit_order_result(config={}, result=order,
                                                           exec_source=EnumExecSource.MANUAL.value)
        else:
            logger.info("check_and_update_manual_live_order@no manual live spot orders.")




if __name__ == '__main__':
    # test_config = {
    #     "id": "1",
    #     "ccy": "ETH-USDT",
    #     "amount": "2000",
    #     "target_price": "3130",
    # }
    #
    # # test_config = {
    # #     "ccy": "ETH-USDT",
    # #     "indicator": "EMA",
    # #     "indicator_val": "120",
    # #     "percentage": "5"
    # # }
    # limit_order_task = SpotLimitOrderTask()
    # limit_order_task.execute_limit_order_task(test_config)
    spot_limit_task = SpotLimitOrderTask()
    # spot_limit_task.check_and_update_auto_live_order()
    # print(spot_limit_task.trade.get_order(
    #     instId=SymbolFormatUtils.get_usdt("SOL-USDT"),
    #     ordId="2101749636187545600",
    # ))
    spot_limit_task.check_and_update_manual_live_order()
