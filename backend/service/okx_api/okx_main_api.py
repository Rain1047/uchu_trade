# okx_api_wrapper.py

from typing import Optional

from backend.data_center.data_object.dao.saving_balance import SavingBalance
from backend.service.decorator import singleton
from backend.service.utils import ConfigUtils, FormatUtils
from account_api import AccountAPIWrapper
from trade_api import TradeAPIWrapper
from market_api import MarketAPIWrapper
from public_data_api import PublicDataAPIWrapper
from funding_api import FundingAPIWrapper
from spread_api import SpreadAPIWrapper


@singleton
class OKXAPIWrapper:
    def __init__(self, env: Optional[str] = 'MARKET'):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.env = env
        self._load_config()

        self.apikey = self.config['apikey_demo'] if self.env == 'DEMO' else self.config['apikey']
        self.secretkey = self.config['secretkey_demo'] if self.env == 'DEMO' else self.config['secretkey']
        self.passphrase = self.config['passphrase']
        self.flag = "1" if self.env == 'DEMO' else "0"

        self.account = AccountAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.trade = TradeAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.market = MarketAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.public_data = PublicDataAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.funding = FundingAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.spread = SpreadAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)

        self._initialized = True

    def _load_config(self):
        self.config = ConfigUtils.get_config()

    @property
    def account_api(self):
        return self.account

    @property
    def trade_api(self):
        return self.trade

    @property
    def market_api(self):
        return self.market

    @property
    def public_data_api(self):
        return self.public_data

    @property
    def funding_api(self):
        return self.funding

    @property
    def spread_api(self):
        return self.spread


if __name__ == '__main__':
    okx_api = OKXAPIWrapper()
    # sb: SavingBalance = FormatUtils.dict2dao(SavingBalance, okx_api.funding_api.get_saving_balance(ccy='ETH').get('data')[0])
    # print(sb.ccy)
    # print(sb.amt)
    #
    # # print(okx_api.funding.purchase_redempt(ccy='ETH', amt='1'))
    #
    # response = okx_api.funding.purchase_redempt(ccy='USDT', amt='2', side='redempt', rate='0.03')
    # print(response)
    #
    # sb: SavingBalance = FormatUtils.dict2dao(SavingBalance,
    #                                          okx_api.funding.get_saving_balance(ccy='ETH').get('data')[0])
    # print(sb.ccy)
    # print(sb.amt)
    okx_api.funding_api.purchase_redempt(ccy='USDT', amt='2', side='redempt', rate='0.03')


