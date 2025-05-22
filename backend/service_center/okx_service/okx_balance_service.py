import logging
from typing import Optional

from backend._constants import OKX_CONSTANTS
from backend._decorators import add_docstring, singleton
from backend._utils import SymbolFormatUtils, LogConfig
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_object_center.account_balance import AccountBalance
from backend.data_object_center.enum_obj import EnumTradeExecuteType, EnumOrderState
from backend.data_object_center.funding_balance import FundingBalance
from backend.data_object_center.saving_balance import SavingBalance
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.spot_trade_config import SpotTradeConfig

logger = LogConfig.get_logger(__name__)


@singleton
class OKXBalanceService:

    def __init__(self):
        logger.info("初始化OKXBalanceService")
        self.okx = OKXAPIWrapper()
        self.trade = self.okx.trade_api
        self.funding = self.okx.funding_api
        self.account = self.okx.account_api
        logger.info("OKXBalanceService初始化完成")

    # [主要方法] 赎回-划转-获取真实的交易账户余额
    @add_docstring("赎回-划转-获取真实的交易账户余额")
    def get_real_account_balance(self, ccy: Optional[str]) -> float:
        try:
            ccy = SymbolFormatUtils.get_base_symbol(ccy)
            # 1.1 reset简单赚币中的币种余额
            self.reset_saving_balance()
            # 1.2 查看简单赚币币种余额
            saving_balance = self.get_saving_balance(symbol=ccy)

            if saving_balance and 'loan_amt' in saving_balance:
                amt = saving_balance['loan_amt']
                # 1.3 赎回
                self.funding.purchase_redempt(ccy=ccy, amt=amt)
                # 1.4 赎回之后再reset一次
                self.reset_saving_balance()
            print(f"{ccy} redempt success.")

            # 2.1 reset资金账户中的币种余额
            self.reset_funding_balance()
            # 2.2 查看资金账户币种余额
            funding_balance = self.get_funding_balance(symbol=ccy)
            if funding_balance and 'availBal' in funding_balance:
                availBal = funding_balance['availBal']
                # 2.3 划转到交易账户
                self.funding.funds_transfer_2exchange(amt=availBal, ccy=ccy)
                # 2.4 划转后再reset一次
                self.reset_funding_balance()
            print(f"{ccy} transfer to exchange success.")

            # 3.1 reset交易账户中的币种余额
            self.reset_account_balance()
            account_balance = AccountBalance.get_by_ccy(ccy)
            if account_balance and 'avail_bal' in account_balance:
                print(f"{ccy} avail_bal: {account_balance['avail_bal']}")
                return float(account_balance['avail_bal'])
            else:
                print(f"{ccy} avail_bal: 0.0")
                return 0.0

        except Exception as e:
            print(f"purchase_redempt error: {e}")
            pass

    @add_docstring("reset资金账户余额")
    def reset_funding_balance(self):
        # 1. 更新现有记录
        response = self.funding.get_balances()
        if response.get('code') == OKX_CONSTANTS.SUCCESS_CODE.value:
            FundingBalance.reset(response)
            return True
        else:
            print(response)
            logger.error(f"list_account_balance error, response: {response.get('code')}, {response.get('message')}")
            return False

    @add_docstring("reset简单赚币账户余额")
    def reset_saving_balance(self) -> bool:
        result = self.funding.get_saving_balance()
        print(result)
        success = SavingBalance.reset(result)
        return success

    @add_docstring("reset交易账户余额")
    def reset_account_balance(self):
        # 1. 更新现有记录
        response = self.account.get_account_balance()
        if response.get('code') == OKX_CONSTANTS.SUCCESS_CODE.value:
            AccountBalance.reset_account_balance(response)
            return True
        else:
            print(response)
            logger.error(f"list_account_balance error, response: {response.get('code')}, {response.get('message')}")
            return False

    @add_docstring("获取赚币中币种余额")
    def get_saving_balance(self, symbol: Optional[str] = '') -> dict:
        try:
            logger.info(f"开始获取余币宝余额 - 币种: {symbol}")
            result = SavingBalance().list_by_condition(condition="ccy", value=symbol)
            logger.info(f"获取余币宝余额响应: {result}")
            
            if result:
                return result[0]
            else:
                return {}
        except Exception as e:
            logger.error(f"获取余币宝余额时发生异常: {str(e)}", exc_info=True)
            return None

    @add_docstring("获取交易账户币种余额")
    def get_funding_balance(self, symbol: Optional[str]):
        try:
            logger.info(f"开始获取资金账户余额 - 币种: {symbol}")
            response = FundingBalance.list_by_condition(condition='ccy', value=symbol)
            logger.info(f"获取资金账户余额响应: {response}")
            
            if response:
                return response[0]
            else:
                return {}
        except Exception as e:
            logger.error(f"获取资金账户余额时发生异常: {str(e)}", exc_info=True)
            return None

    @add_docstring("获取交易账户余额列表")
    def list_account_balance(self):
        try:
            logger.info("开始获取账户余额列表")
            response = self.account.get_account_balance()
            logger.info(f"获取账户余额响应: {response}")
            
            if response.get('code') != '0':
                error_msg = f"获取账户余额失败 - 错误码: {response.get('code')}, 错误信息: {response.get('msg')}"
                logger.error(error_msg)
                return None
                
            return response.get('data', [])
        except Exception as e:
            logger.error(f"获取账户余额时发生异常: {str(e)}", exc_info=True)
            return None

    def list_balance_config(ccy):
        print(SpotTradeConfig.list_by_ccy_and_type(ccy))


if __name__ == '__main__':
    # list_account_balance()
    pass
