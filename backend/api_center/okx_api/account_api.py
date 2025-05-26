# account_api_wrapper.py

import okx.Account as Account
from typing import Dict, Optional
from backend._decorators import add_docstring


class AccountAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.accountAPI = Account.AccountAPI(
            api_key=apikey,
            api_secret_key=secretkey,
            passphrase=passphrase,
            use_server_time=False,
            flag=flag,
            debug=False,
        )

    @add_docstring("获取账户余额")
    def get_account_balance(self) -> Dict:
        return self.accountAPI.get_account_balance()

    @add_docstring("账户持仓信息 - 期货交易")
    def get_positions(self, instType='', instId: Optional[str] = '') -> Dict:
        return self.accountAPI.get_positions(instId=instId, instType=instType)

    @add_docstring("账户历史持仓信息")
    def get_positions_history(self, instType: Optional[str] = '', instId: Optional[str] = '',
                              mgnMode: Optional[str] = '', type: Optional[str] = '',
                              posId: Optional[str] = '', after: Optional[str] = '',
                              before: Optional[str] = '', limit: Optional[str] = '') -> Dict:
        return self.accountAPI.get_positions_history(instType=instType, instId=instId, mgnMode=mgnMode, type=type,
                                                     posId=posId, after=after, before=before, limit=limit)

    @add_docstring("账户账单流水")
    def get_account_bills_archive(self) -> Dict:
        return self.accountAPI.get_account_bills_archive()


if __name__ == '__main__':
    pass
