from typing import Optional

from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.object_center._object_dao.account_balance import AccountBalance


class OKXMainService:

    def __init__(self):
        self.okx = OKXAPIWrapper()
        self.trade = self.okx.trade_api
        self.funding = self.okx.funding_api

    # [主要方法] 赎回-划转-获取真实的交易账户余额
    def okx_get_real_account_balance(self, ccy: Optional[str]) -> float:
        try:
            ccy = SymbolFormatUtils.get_base_symbol(ccy)
            # 1.1 reset简单赚币中的币种余额
            reset_saving_balance()
            # 1.2 查看简单赚币币种余额
            saving_balance = get_saving_balance(symbol=ccy)

            if saving_balance and 'loan_amt' in saving_balance:
                amt = saving_balance['loan_amt']
                # 1.3 赎回
                self.funding.purchase_redempt(ccy=ccy, amt=amt)
                # 1.4 赎回之后再reset一次
                reset_saving_balance()
            print(f"{ccy} redempt success.")

            # 2.1 reset资金账户中的币种余额
            reset_funding_balance()
            # 2.2 查看资金账户币种余额
            funding_balance = get_funding_balance(symbol=ccy)
            if funding_balance and 'availBal' in funding_balance:
                availBal = funding_balance['availBal']
                # 2.3 划转到交易账户
                self.funding.funds_transfer_2exchange(amt=availBal, ccy=ccy)
                # 2.4 划转后再reset一次
                reset_funding_balance()
            print(f"{ccy} transfer to exchange success.")

            # 3.1 reset交易账户中的币种余额
            reset_account_balance()
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
