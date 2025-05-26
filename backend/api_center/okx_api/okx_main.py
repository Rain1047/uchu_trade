from typing import Optional

from backend._decorators import singleton
from backend._utils import ConfigUtils, LogConfig
from backend.api_center.okx_api.account_api import AccountAPIWrapper
from backend.api_center.okx_api.trade_api import TradeAPIWrapper
from backend.api_center.okx_api.market_api import MarketAPIWrapper
from backend.api_center.okx_api.public_data_api import PublicDataAPIWrapper
from backend.api_center.okx_api.funding_api import FundingAPIWrapper
from backend.api_center.okx_api.spread_api import SpreadAPIWrapper
from backend.data_object_center.enum_obj import *

logger = LogConfig.get_logger(__name__)

@singleton
class OKXAPIWrapper:
    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        if hasattr(self, '_initialized') and self._initialized:
            logger.info(f"OKXAPIWrapper已经初始化，使用环境: {self.env}")
            return

        self.env = env if env is not None else EnumTradeEnv.DEMO.value
        logger.info(f"初始化OKXAPIWrapper - 环境: {self.env}")
        
        self._load_config()
        logger.info("配置加载完成")

        self.apikey = self.config['okx_api_key_demo'] \
            if self.env == EnumTradeEnv.DEMO.value else self.config['okx_api_key']
        self.secretkey = self.config['okx_secret_key_demo'] \
            if self.env == EnumTradeEnv.DEMO.value else self.config['okx_secret_key']
        self.passphrase = self.config['passphrase']
        self.flag = "1" if self.env == EnumTradeEnv.DEMO.value else "0"
        
        logger.info(f"API配置 - 环境: {self.env}, 模拟交易: {self.flag}")

        try:
            self.account = AccountAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
            self.trade = TradeAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
            self.market = MarketAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
            self.public_data = PublicDataAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
            self.funding = FundingAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
            self.spread = SpreadAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
            
            logger.info("所有API组件初始化完成")
        except Exception as e:
            logger.error(f"初始化API组件时发生错误: {str(e)}", exc_info=True)
            raise

        self._initialized = True
        logger.info(f"{self.env} OKX API 初始化完成")

    def _load_config(self):
        try:
            self.config = ConfigUtils.get_config()
            logger.debug("配置加载成功")
        except Exception as e:
            logger.error(f"加载配置时发生错误: {str(e)}", exc_info=True)
            raise

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
    print(okx_api.funding.purchase_redempt(ccy='ETH', amt='1'))
    #
    # response = okx_api.funding.purchase_redempt(ccy='USDT', amt='2', side='redempt', rate='0.03')
    # print(response)
    #
    # sb: SavingBalance = FormatUtils.dict2dao(SavingBalance,
    #                                          okx_api.funding.get_saving_balance(ccy='ETH').get('data')[0])
    # print(sb.ccy)
    # print(sb.amt)
    # okx_api.funding_api.purchase_redempt(ccy='USDT', amt='2', side='redempt', rate='0.03')




