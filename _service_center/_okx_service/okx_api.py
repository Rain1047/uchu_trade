import okx.Account as Account
import okx.Trade as Trade
import okx.MarketData as Market
from typing import Optional, Dict

from _data_center.data_object.dao.order_detail import OrderDetailDB
from _data_center.data_object.enum_obj import *
from _service_center.data_api import *

dbApi = DataAPIWrapper()


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        env = kwargs.get('env', EnumTradeEnv.MARKET.value)
        if env not in instances:
            instances[env] = cls(*args, **kwargs)
        return instances[env]

    return get_instance


@singleton
class OKXAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.env = env
        self.config_file_path = '../../config.json'
        self._load_config()

        self.apikey = self.config['apikey_demo'] \
            if self.env == EnumTradeEnv.DEMO.value else self.config['apikey']
        self.secretkey = self.config['secretkey_demo'] \
            if self.env == EnumTradeEnv.DEMO.value else self.config['secretkey']
        self.passphrase = self.config['passphrase']
        self.flag = "1" if self.env == EnumTradeEnv.DEMO.value else "0"
        self._initialize_account_api()
        self._initialize_trade_api()
        self._initialize_market_api()

        self._initialized = True
        print("{} OKX API initialized.".format(self.env))

    def _load_config(self):
        with open(self.config_file_path, 'r') as config_file:
            self.config = json.load(config_file)

    # 初始化账户API
    def _initialize_account_api(self):
        self.accountAPI = Account.AccountAPI(self.apikey, self.secretkey, self.passphrase, False, self.flag)

    # 初始化交易API
    def _initialize_trade_api(self):
        self.tradeAPI = Trade.TradeAPI(self.apikey, self.secretkey, self.passphrase, False, self.flag)

    # 初始化行情API
    def _initialize_market_api(self):
        self.marketAPI = Market.MarketAPI(self.apikey, self.secretkey, self.passphrase, False, self.flag)

    # 账户余额
    def get_account_balance(self) -> Dict:
        return self.accountAPI.get_account_balance()

    # 账户持仓信息 - 期货交易
    def get_positions(self) -> Dict:
        return self.accountAPI.get_positions()

    # 账户历史持仓信息
    def get_positions_history(self) -> Dict:
        return self.accountAPI.get_positions_history()

    # 获取成交明细（近三个月）
    # 获取近3个月订单成交明细信息
    def get_trade_fills_history(self, instType: str, **kwargs) -> Dict:
        return self.tradeAPI.get_fills_history(instType=instType, **kwargs)

    # 获取历史订单记录（近三个月）
    # 获取最近3个月挂单，且完成的订单数据，包括3个月以前挂单，但近3个月才成交的订单数据。按照订单创建时间倒序排序。
    def get_orders_history_archive(self, instType: Optional[str] = EnumInstanceType.SPOT.value, **kwargs) -> json:
        # 查询币币历史订单（3月内）
        return self.tradeAPI.get_orders_history_archive(instType=instType, **kwargs)

    # 获取订单信息
    def get_order(self, instId: str, ordId: str) -> Dict:
        return self.tradeAPI.get_order(instId=instId, ordId=ordId)

    # 通过Ticker Symbol来获取行情
    def get_ticker(self, instId: str):
        return self.marketAPI.get_ticker(instId=instId)

    # 通过Ticker Symbol获取k线
    def get_candlesticks(self, instId: str, bar: Optional[str] = EnumTimeFrame.D1_L.value) -> Dict:
        return self.marketAPI.get_candlesticks(instId=instId, bar=bar)

    def get_candlesticks_df(self, instId: str, bar: Optional[str] = EnumTimeFrame.D1_L.value) -> pd.DataFrame:
        return FormatUtils.dict2df(self.marketAPI.get_candlesticks(instId=instId, bar=bar))


# 示例用法
if __name__ == "__main__":
    okx = OKXAPIWrapper()
    # print(okx.get_account_balance())
    # print(okx.get_positions())
    # print(okx.get_positions_history())
    # print(okx.get_trade_fills_history(instType="SPOT"))
    # print(okx.get_orders_history_archive())
    # Convert dictionary to OrderDetailDB instance
    # order_detail_instance = dict_to_order_detail(OrderDetailDB, order_details_dict)
    dbApi.insert_order_details(okx.get_orders_history_archive(), OrderDetailDB)
    # try:
    #     store_data_to_db(okx.get_orders_history_archive())
    #     print("Data stored successfully.")
    # except Exception as e:
    #     print(f"Error storing data: {e}")
    # finally:
    #     print("Done.")
    # print(okx.get_order(instId="BTC-USDT", ordId="680800019749904384"))
    # print(okx.get_candlesticks(instId="BTC-USDT", bar="1H"))
