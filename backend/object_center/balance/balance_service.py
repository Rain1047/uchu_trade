from typing import List, Any, Dict

from backend._utils import SymbolFormatUtils
from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center._object_dao.funding_balance import FundingBalance
from backend.object_center._object_dao.saving_balance import SavingBalance
from backend.object_center._object_dao.spot_trade_config import SpotTradeConfig
from backend.object_center.balance.balance_request import UpdateAccountBalanceSwitchRequest


class BalanceService:
    """
    balance service
    """

    @staticmethod
    def update_account_balance_switch(request: UpdateAccountBalanceSwitchRequest) -> bool:
        return AccountBalance.update_switch(ccy=request.ccy, type=request.type, switch=request.switch)

    @staticmethod
    def save_update_balance_config(config_list: List[Dict[str, Any]]) -> bool:
        return SpotTradeConfig.create_or_update(config_list)


if __name__ == '__main__':
    balance_service = BalanceService()
    request = UpdateAccountBalanceSwitchRequest(ccy="ETH-USDT", type="limit_order", switch="true")
    request.ccy = SymbolFormatUtils.get_base_symbol(request.ccy)
    success = balance_service.update_account_balance_switch(request)
    print(success)
