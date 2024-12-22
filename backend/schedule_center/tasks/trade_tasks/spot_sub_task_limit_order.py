from backend._decorators import singleton
from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.object_center._object_dao.spot_algo_order_record import SpotAlgoOrderRecord
from backend.object_center.enum_obj import EnumTdMode, EnumAlgoOrdType, EnumSide, EnumOrdType, EnumAutoTradeConfigType, \
    EnumState
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_ticker_service import OKXTickerService


@singleton
class SpotSubTaskLimitOrder:

    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()

    # [调度子任务] 根据配置进行限价委托
    def execute_limit_order_task(self, config: dict):

        ccy = config.get('ccy')
        target_price = config.get('target_price')
        if not target_price:
            target_price = self.okx_ticker_service.get_target_indicator_latest_price(
                instId=SymbolFormatUtils.get_usdt(ccy),
                bar='1D',
                indicator=config.get('indicator'),
                indicator_val=config.get('indicator_val')
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
        self.save_limit_order_result(config, result)
        print(result)

    @staticmethod
    def save_limit_order_result(config: dict, result: dict):
        stop_loss_data = {
            'ccy': config.get('ccy'),
            'type': EnumAutoTradeConfigType.LIMIT_ORDER.value,
            'config_id': config.get('id'),
            'sz': config.get('sz'),
            'amount': config.get('amount'),
            'target_price': config.get('target_price'),
            'ordId': result.get('data')[0].get('ordId'),
            'status': EnumState.LIVE.value
        }
        success = SpotAlgoOrderRecord.insert(stop_loss_data)
        print(f"Insert limit order: {'success' if success else 'failed'}")

    def update_limit_order_status(self):
        live_order_list = SpotAlgoOrderRecord.list_by_status(EnumState.LIVE.value)
        if len(live_order_list) > 1:
            for live_order in live_order_list:
                latest_order = self.trade.get_order(instId=SymbolFormatUtils.get_usdt(live_order.get('ccy')),
                                                    ordId=live_order.get('ordId'))
                latest_status = latest_order.get('data')[0].get('state')
                if latest_order.get('data')[0].get('state') != EnumState.LIVE.value:
                    SpotAlgoOrderRecord.update_status_by_ord_id(live_order.get('ordId'), latest_status)


if __name__ == '__main__':
    test_config = {
        "id": "1",
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
    limit_order_task = SpotSubTaskLimitOrder()
    limit_order_task.execute_limit_order_task(test_config)
