import okx.Account as Account
import okx.Trade as Trade
import okx.MarketData as Market
import okx.PublicData as PublicData
import okx.Funding as Funding
from typing import Optional, Dict

from backend.data_center.data_object.dao.order_detail import OrderDetailDB
from backend.data_center.data_object.enum_obj import *
from backend.service.data_api import *

dbApi = DataAPIWrapper()


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        env = kwargs.get('env', EnumTradeEnv.MARKET.value)
        if env not in instances:
            instances[env] = cls(*args, **kwargs)
        return instances[env]

    return get_instance


def add_docstring(docstring: str):
    def decorator(func):
        func.__doc__ = docstring
        return func

    return decorator


class AccountAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取账户余额")
    def get_account_balance(self) -> Dict:
        return self.accountAPI.get_account_balance()

    @add_docstring("账户持仓信息 - 期货交易")
    def get_positions(self) -> Dict:
        return self.accountAPI.get_positions()

    @add_docstring("账户历史持仓信息")
    def get_positions_history(self) -> Dict:
        return self.accountAPI.get_positions_history()

    @add_docstring("账户账单流水")
    def get_account_bills_archive(self) -> Dict:
        return self.accountAPI.get_account_bills_archive()


class TradeAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取成交明细（近三个月）")
    def get_trade_fills_history(self, instType: str, **kwargs) -> Dict:
        return self.tradeAPI.get_fills_history(instType=instType, **kwargs)

    @add_docstring("获取历史订单记录（近三个月）")
    def get_orders_history_archive(self, instType: Optional[str] = EnumInstanceType.SPOT.value, **kwargs) -> json:
        return self.tradeAPI.get_orders_history_archive(instType=instType, **kwargs)

    @add_docstring("获取订单信息")
    def get_order(self, instId: str, ordId: str) -> Dict:
        return self.tradeAPI.get_order(instId=instId, ordId=ordId)

    @add_docstring("下单")
    def place_order(self, instId: str,
                    sz: str,
                    side: str,
                    posSide: str,
                    ordType: str,
                    slTriggerPx: str,
                    px: Optional[str] = '',
                    slOrdPx: Optional[str] = "-1",
                    tdMode: Optional[str] = EnumTdMode.CASH.value,
                    clOrdId: Optional[str] = '',
                    ) -> Dict:
        return self.tradeAPI.place_order(instId=instId, tdMode=tdMode, sz=sz, px=px,
                                         side=side, posSide=posSide, ordType=ordType,
                                         slTriggerPx=slTriggerPx, slOrdPx=slOrdPx,
                                         clOrdId=clOrdId)

    @add_docstring("策略下单")
    def place_algo_order(self, instId: str,
                         sz: str,
                         posSide: Optional[str] = '',
                         tpTriggerPx: Optional[str] = '',
                         tpOrdPx: Optional[str] = '',
                         clOrdId: Optional[str] = '',
                         slTriggerPx: Optional[str] = '',
                         slOrdPx: Optional[str] = '',
                         side: Optional[str] = EnumSide.BUY.value,
                         tdMode: Optional[str] = EnumTdMode.CASH.value,
                         ordType: Optional[str] = EnumOrdType.CONDITIONAL.value,
                         ) -> Dict:
        return self.tradeAPI.place_algo_order(instId=instId, tdMode=tdMode, sz=sz,
                                              side=side, posSide=posSide,
                                              ordType=ordType,
                                              algoClOrdId=clOrdId,
                                              slTriggerPx=slTriggerPx,
                                              slOrdPx=slOrdPx)


class FundingAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取币种列表")
    def get_currencies(self) -> Dict:
        return self.fundingAPI.get_currencies()


class MarketAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.marketAPI = Market.MarketAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("通过Ticker Symbol来获取行情")
    def get_ticker(self, instId: str):
        return self.marketAPI.get_ticker(instId=instId)

    @add_docstring("通过Ticker Symbol获取k线")
    def get_candlesticks(self, instId: str, bar: Optional[str] = EnumTimeFrame.D1_L.value) -> Dict:
        return self.marketAPI.get_candlesticks(instId=instId, bar=bar)

    @add_docstring("通过Ticker Symbol获取k线，并返回DataFrame")
    def get_candlesticks_df(self, instId: str, bar: Optional[str] = EnumTimeFrame.D1_L.value) -> pd.DataFrame:
        return FormatUtils.dict2df(self.marketAPI.get_candlesticks(instId=instId, bar=bar))


@singleton
class PublicDataAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.publicAPI = PublicData.PublicAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("张币转换")
    def get_convert_contract_coin(self, instId: str, px: str, sz: str, unit: Optional[str] = "usds"):
        self.publicAPI.get_convert_contract_coin(instId=instId, sz=sz, px=px, unit=unit)


@singleton
class OKXAPIWrapper:
    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.env = env
        self._load_config()

        self.apikey = self.config['apikey_demo'] if self.env == EnumTradeEnv.DEMO.value else self.config['apikey']
        self.secretkey = self.config['secretkey_demo'] if self.env == EnumTradeEnv.DEMO.value else self.config[
            'secretkey']
        self.passphrase = self.config['passphrase']
        self.flag = "1" if self.env == EnumTradeEnv.DEMO.value else "0"

        self.account = AccountAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.trade = TradeAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.market = MarketAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.publicData = PublicDataAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)
        self.funding = FundingAPIWrapper(self.apikey, self.secretkey, self.passphrase, self.flag)

        self._initialized = True
        print("{} OKX API initialized.".format(self.env))

    def _load_config(self):
        self.config = ConfigUtils.get_config()


# 示例用法
if __name__ == "__main__":
    okx = OKXAPIWrapper()
    okx_demo = OKXAPIWrapper(env=EnumTradeEnv.DEMO.value)
    # print(okx.apikey)
    # print(okx_demo.apikey)
    '''
    Account
    '''
    # print(okx.account.get_account_balance())
    # print(okx.account.get_positions())
    # print(okx.account.get_positions_history())
    # print(okx.account.get_account_bills_archive())
    '''
    Trade
    '''
    # print(okx.trade.get_trade_fills_history(instType="SPOT"))
    # print(okx.trade.get_orders_history_archive())
    dbApi.insert_order_details(okx.trade.get_orders_history_archive(), OrderDetailDB)

    # 现货模式限价单
    # result = okx_demo.trade.place_order(
    #     instId="BTC-USDT",
    #     tdMode="cash",
    #     side="buy",
    #     ordType="limit",
    #     # px="2.15",  # 委托价格
    #     sz="2",  # 委托数量
    #     slTriggerPx="55000",
    #     slOrdPx="54000"
    # )
    #
    # result = okx_demo.trade.place_algo_order(
    #     instId="ETH-USDT",
    #     tdMode="cash",
    #     side="sell",
    #     ordType="conditional",
    #     sz="0.1",
    #     tpTriggerPx="",
    #     tpOrdPx="",
    #     slTriggerPx="2400",
    #     slOrdPx="2300"
    # )
    # print(result)

    '''
    Market
    '''
    # print(okx.market.get_ticker(instId="BTC-USDT"))
    # print(okx.market.get_candlesticks(instId="BTC-USDT", bar="1H"))

    '''
    Funding
    '''
    # print(okx.funding.get_currencies())
