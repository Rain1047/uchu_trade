from typing import List, Any, Dict

from backend._utils import SymbolFormatUtils
from backend.data_object_center.account_balance import AccountBalance
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.controller_center.balance.balance_request import UpdateAccountBalanceSwitchRequest, TradeConfig, \
    TradeConfigExecuteHistory
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService


class BalanceService:

    def __init__(self):
        self.okx_balance_service = OKXBalanceService()

    """
    balance service
    """

    @staticmethod
    def update_account_balance_switch(request: UpdateAccountBalanceSwitchRequest) -> bool:
        return AccountBalance.update_switch(ccy=SymbolFormatUtils.get_base_symbol(request.ccy),
                                            type=request.type,
                                            switch=request.switch)

    @staticmethod
    def batch_create_or_update_balance_configs(config_list: List[Dict[str, Any]]) -> bool:
        return SpotTradeConfig.batch_create_or_update(config_list)

    @staticmethod
    def list_trade_configs(ccy: str, type_: str) -> List[Dict]:
        """查询交易配置"""
        return SpotTradeConfig.list_configs_by_ccy_and_type(ccy, type_)

    def list_account_balance(self):
        return self.okx_balance_service.list_account_balance()

    @staticmethod
    def list_config_execute_records(config_execute_history_request: TradeConfigExecuteHistory):
        return SpotAlgoOrderRecord.list_spot_algo_order_record_by_conditions(config_execute_history_request)


if __name__ == '__main__':
    balance_service = BalanceService()
    request = UpdateAccountBalanceSwitchRequest(ccy="ETH-USDT", type="limit_order", switch="true")
    request.ccy = SymbolFormatUtils.get_base_symbol(request.ccy)
    success = balance_service.update_account_balance_switch(request)
    print(success)
