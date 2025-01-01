import logging

from backend._decorators import singleton
from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.data_object_center.account_balance import AccountBalance
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.enum_obj import EnumTdMode, EnumAlgoOrdType, EnumSide, EnumAlgoOrderState, \
    EnumTradeExecuteType, EnumExecSource
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_order_service import OKXOrderService
from backend.service_center.okx_service.okx_ticker_service import OKXTickerService

logger = logging.getLogger(__name__)


@singleton
class SpotStopLossTask:

    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()
        self.okx_record_service = OKXOrderService()

    def check_and_update_auto_live_stop_loss_orders(self):
        # 1. get all unfinished algo orders
        live_stop_loss_order_list = SpotAlgoOrderRecord.list_live_auto_stop_loss_orders()
        if len(live_stop_loss_order_list) > 0:
            for live_stop_loss_order in live_stop_loss_order_list:
                algoId = live_stop_loss_order.get('algoId')
                # 2. check algo order status
                latest_algo_order_result = self.trade.get_algo_order(algoId=algoId)
                if latest_algo_order_result and latest_algo_order_result.get('code') == '0':
                    latest_algo_order = latest_algo_order_result.get('data')[0]
                    print(f"algoId:{algoId} latest status is {latest_algo_order.get('state')}.")
                    if latest_algo_order.get('state') == EnumAlgoOrderState.CANCELED.value:
                        SpotAlgoOrderRecord.update_status_by_algo_id(algoId, EnumAlgoOrderState.CANCELED.value)
                    if latest_algo_order.get('state') == EnumAlgoOrderState.EFFECTIVE.value:
                        SpotAlgoOrderRecord.update_status_by_algo_id(algoId, EnumAlgoOrderState.EFFECTIVE.value)
                        SpotTradeConfig.minus_exec_nums(id=live_stop_loss_order.get('config_id'))
                    elif latest_algo_order.get('state') == EnumAlgoOrderState.LIVE.value:
                        logger.info(f"check_and_update_auto_spot_live_order@ {latest_algo_order} is live")
                        spot_trade_config = SpotTradeConfig.get_effective_spot_config_by_id(
                            live_stop_loss_order.get('config_id'))
                        if spot_trade_config:
                            self.update_stop_loss_order(spot_trade_config, latest_algo_order)
                    else:
                        logger.info(
                            f"check_and_update_auto_spot_live_order@ {latest_algo_order} is {latest_algo_order.get('state')}.")
        else:
            logger.info("check_and_update_auto_spot_live_algo_order@no auto live spot algo orders.")

    def update_stop_loss_order(self, spot_trade_config, latest_algo_order):
        target_price = spot_trade_config.get('target_price')
        if not target_price:
            # 计算目标止损价, 根据indicator获取实时价格
            target_price = self.okx_ticker_service.get_target_indicator_latest_price_by_spot_config(
                config=spot_trade_config
            )
        print(f"update_stop_loss_order@target price: {target_price}")
        # 获取目标止损仓位
        target_amount = spot_trade_config.get('amount')
        sz = ''
        if not target_amount:
            real_sz = self.okx_balance_service.get_real_account_balance(ccy=spot_trade_config.get('ccy'))
            pct = spot_trade_config.get('percentage')
            sz = str(round(float(real_sz) * int(pct) / 100, 6))
        else:
            sz = str(round(float(target_amount) / float(target_price), 6))

        self.trade.amend_algo_order(
            instId=SymbolFormatUtils.get_usdt(spot_trade_config.get('ccy')),
            algoId=latest_algo_order.get('algoId'),
            newSz=sz,
            newSlTriggerPx=str(target_price),
            newTpOrdPx='-1'
        )

    # [调度子任务] 止损委托
    def execute_stop_loss_task(self, config: dict):
        try:
            ccy = config.get('ccy')
            # 获取目标止损价格
            target_price = config.get('target_price')
            if not target_price:
                # 计算目标止损价, 根据indicator获取实时价格
                target_price = self.okx_ticker_service.get_target_indicator_latest_price_by_spot_config(
                    config=config
                )
            # 获取目标止损仓位
            target_amount = config.get('amount')
            sz = ''
            if not target_amount:
                real_sz = self.okx_balance_service.get_real_account_balance(ccy=ccy)
                pct = config.get('percentage')
                sz = str(round(float(real_sz) * int(pct) / 100, 6))
            else:
                sz = str(round(float(target_amount) / float(target_price), 6))
            config['sz'] = sz
            config['amount'] = str(target_amount)
            config['target_price'] = str(target_price)

            result = self.trade.place_algo_order(
                instId=SymbolFormatUtils.get_usdt(ccy),
                tdMode=EnumTdMode.CASH.value,
                side=EnumSide.SELL.value,
                ordType=EnumAlgoOrdType.CONDITIONAL.value,
                sz=sz,
                slTriggerPx=str(target_price),  # 止损触发价格
                slOrdPx='-1'
            )
            if result and result.get('code') == '0':
                result = result.get('data')[0]
                self.save_stop_loss_result(config, result)
            SpotTradeConfig.minus_exec_nums(config.get('id'))
            print(f"execute_stop_loss_task@config: {config.get('id')} execute result: {result}")
        except Exception as e:
            print(f"execute_stop_loss_task@e_handle_trade_result error: {e}")

    @staticmethod
    def save_stop_loss_result(config: dict, result: dict):
        stop_loss_data = {
            'ccy': config.get('ccy') if config else
            SymbolFormatUtils.get_base_symbol(result.get('instId')),
            'type': EnumTradeExecuteType.STOP_LOSS.value,
            'config_id': config.get('id') if config else '',
            'sz': config.get('sz') if config else result.get('sz'),
            'amount': config.get('amount') if config else
            str(float(result.get('sz')) * float(result.get('slTriggerPx'))),
            'target_price': config.get('target_price') if config else
            result.get('slTriggerPx'),
            'algoId': result.get('algoId'),
            'status': EnumAlgoOrderState.LIVE.value,
            'exec_source': EnumExecSource.AUTO.value if config else EnumExecSource.MANUAL.value,
        }
        success = SpotAlgoOrderRecord.insert_or_update(stop_loss_data)
        print(f"Insert stop loss: {'success' if success else 'failed'}")

    def update_stop_loss_status(self):
        live_order_list = SpotAlgoOrderRecord.list_by_status(EnumAlgoOrderState.LIVE.value)
        if len(live_order_list) > 0:
            for live_order in live_order_list:
                latest_order = self.trade.get_algo_order(algoId=live_order.get('algoId'))
                latest_status = latest_order.get('data')[0].get('state')
                if latest_order.get('data')[0].get('state') != EnumAlgoOrderState.LIVE.value:
                    success = SpotAlgoOrderRecord.update_status_by_algo_id(live_order.get('algoId'), latest_status)
                    print(f"Update stop loss status: {'success' if success else 'failed'}")
                print(f"{live_order.get('algoId')}: {latest_status}")

    def process_new_auto_stop_loss_task(self):
        activate_stop_loss_ccy_list = AccountBalance.list_activate_stop_loss_ccy()
        if len(activate_stop_loss_ccy_list) > 0:
            for ccy in activate_stop_loss_ccy_list:
                stop_loss_configs = SpotTradeConfig.get_effective_and_unfinished_stop_loss_configs_by_ccy(ccy)
                if len(stop_loss_configs) > 0:
                    for config in stop_loss_configs:
                        print(f"process_new_auto_stop_loss_task@config: {config}")
                        self.execute_stop_loss_task(config)
                    print(f"process_new_auto_stop_loss_task@stop_loss_configs execute finished.")
            print(f"process_new_auto_stop_loss_task@activate_stop_loss_ccy_list execute finished.")
        else:
            print(f"process_new_auto_stop_loss_task@activate_stop_loss_ccy_list is empty.")

    def check_and_update_manual_live_stop_loss_orders(self):
        # # [查看数据库] 获取所有未完成的订单
        # manual_live_stop_loss_order_list = SpotAlgoOrderRecord.list_live_manual_spot_stop_loss_orders()
        # if len(manual_live_stop_loss_order_list) > 0:
        #     for manual_live_stop_loss_order in manual_live_stop_loss_order_list:
        #         latest_algo_order = self.trade.get_algo_order(algoId=manual_live_stop_loss_order.get('algoId'))
        #         if latest_algo_order and latest_algo_order.get('code') == '0':
        #             if latest_algo_order.get('data')[0].get('state') != EnumAlgoOrderState.LIVE.value:
        #                 SpotAlgoOrderRecord.update_status_by_algo_id(manual_live_stop_loss_order.get('algoId'),
        #                                                              latest_algo_order.get('data')[0].get('state'))
        # [调用接口] 获取所有未完成的订单
        algo_order_list_result = self.trade.order_algos_list(
            instType="SPOT", ordType="conditional")
        if algo_order_list_result and algo_order_list_result.get('code') == '0':
            algo_order_list = algo_order_list_result.get('data')
            if len(algo_order_list) > 0:
                for algo_order in algo_order_list:
                    if algo_order.get('side') != EnumSide.SELL.value:
                        continue
                    exist_algo_order = SpotAlgoOrderRecord.get_by_algo_id(algo_order.get('algoId'))
                    if exist_algo_order:
                        continue
                    else:
                        self.okx_record_service.save_or_update_limit_order_result(config={}, result=algo_order)
        else:
            logger.info("check_and_update_manual_live_order@no manual live spot orders.")


if __name__ == '__main__':
    # pass
    # test_config = {
    #     "ccy": "ETH-USDT",
    #     "amount": "1000",
    #     "target_price": "3000",
    # }

    # test_config = {
    #     "ccy": "ETH-USDT",
    #     "indicator": "EMA",
    #     "indicator_val": "120",
    #     "percentage": "5"
    # }
    stop_loss_executor = SpotStopLossTask()
    stop_loss_executor.check_and_update_manual_live_stop_loss_orders()
