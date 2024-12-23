from backend._decorators import singleton
from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.enum_obj import EnumTdMode, EnumAlgoOrdType, EnumSide, EnumStateAlgoOrder, \
    EnumAutoTradeConfigType
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_ticker_service import OKXTickerService


@singleton
class SpotSubTaskStopLoss:

    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()

    # [调度子任务] 止损委托
    def execute_stop_loss_task(self, config: dict):
        ccy = config.get('ccy')
        # 获取目标止损价格
        target_price = config.get('target_price')
        if not target_price:
            # 计算目标止损价, 根据indicator获取实时价格
            target_price = self.okx_ticker_service.get_target_indicator_latest_price(
                instId=SymbolFormatUtils.get_usdt(ccy),
                bar='1D',  # 固定
                indicator=config.get('indicator'),
                indicator_val=config.get('indicator_val')
            )
        print(f"target price: {target_price}")
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
        print(f"sz: {sz}")

        result = self.trade.place_algo_order(
            instId=SymbolFormatUtils.get_usdt(ccy),
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.SELL.value,
            ordType=EnumAlgoOrdType.CONDITIONAL.value,
            sz=sz,
            slTriggerPx=str(target_price),  # 止损触发价格
            slOrdPx='-1'
        )
        self.save_stop_loss_result(config, result)
        SpotTradeConfig.update_spot_config_exec_nums(config)
        print(result)

    @staticmethod
    def save_stop_loss_result(config: dict, result: dict):
        stop_loss_data = {
            'ccy': config.get('ccy'),
            'type': EnumAutoTradeConfigType.STOP_LOSS.value,
            'config_id': config.get('id'),
            'sz': config.get('sz'),
            'amount': config.get('amount'),
            'target_price': config.get('target_price'),
            'algoId': result.get('data')[0].get('algoId'),
            'status': EnumStateAlgoOrder.LIVE.value
        }
        success = SpotAlgoOrderRecord.insert(stop_loss_data)
        print(f"Insert stop loss: {'success' if success else 'failed'}")

    def update_stop_loss_status(self):
        live_order_list = SpotAlgoOrderRecord.list_by_status(EnumStateAlgoOrder.LIVE.value)
        if len(live_order_list) > 0:
            for live_order in live_order_list:
                latest_order = self.trade.get_algo_order(algoId=live_order.get('algoId'))
                latest_status = latest_order.get('data')[0].get('state')
                if latest_order.get('data')[0].get('state') != EnumStateAlgoOrder.LIVE.value:
                    success = SpotAlgoOrderRecord.update_status_by_algo_id(live_order.get('algoId'), latest_status)
                    print(f"Update stop loss status: {'success' if success else 'failed'}")
                print(f"{live_order.get('algoId')}: {latest_status}")


if __name__ == '__main__':
    pass
    test_config = {
        "ccy": "ETH-USDT",
        "amount": "1000",
        "target_price": "3000",
    }

    # test_config = {
    #     "ccy": "ETH-USDT",
    #     "indicator": "EMA",
    #     "indicator_val": "120",
    #     "percentage": "5"
    # }
    stop_loss_executor = SpotSubTaskStopLoss()
    stop_loss_executor.update_stop_loss_status()
