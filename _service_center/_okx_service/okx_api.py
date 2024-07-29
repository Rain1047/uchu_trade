import okx.Account as Account
import okx.Trade as Trade
import json
from typing import Optional
from _data_center.data_object.enum_obj import *


class OKXAPIWrapper:

    def __init__(self, env: Optional[str] = EnumTradeEnv.MARKET.value):
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

    def _load_config(self):
        with open(self.config_file_path, 'r') as config_file:
            self.config = json.load(config_file)

    def _initialize_account_api(self):
        print("account api initialized.")
        self.accountAPI = Account.AccountAPI(self.apikey, self.secretkey, self.passphrase, False, self.flag)

    def _initialize_trade_api(self):
        self.tradeAPI = Trade.TradeAPI(self.apikey, self.secretkey, self.passphrase, False, self.flag)

    # 账户余额
    def get_account_balance(self) -> json:
        return self.accountAPI.get_account_balance()

    # 账户持仓信息 - 期货交易
    def get_positions(self) -> json:
        return self.accountAPI.get_positions()

    # 账户历史持仓信息
    def get_positions_history(self) -> json:
        return self.accountAPI.get_positions_history()

    # 获取成交明细（近三个月）
    # 获取近3个月订单成交明细信息
    def get_trade_fills_history(self, instType: str, **kwargs) -> json:
        return self.tradeAPI.get_fills_history(instType=instType, **kwargs)

    # 获取历史订单记录（近三个月）
    # 获取最近3个月挂单，且完成的订单数据，包括3个月以前挂单，但近3个月才成交的订单数据。按照订单创建时间倒序排序。
    def get_orders_history_archive(self, instType: str, **kwargs) -> json:
        # 查询币币历史订单（3月内）
        return self.tradeAPI.get_orders_history_archive(instType=instType, **kwargs)

    # 获取订单信息
    def get_order(self, instId: str, ordId: str) -> json:
        return self.tradeAPI.get_order(instId=instId, ordId=ordId)


# 示例用法
if __name__ == "__main__":
    okx = OKXAPIWrapper(env=EnumTradeEnv.MARKET.value)
    # print(okx.get_account_balance())
    # print(okx.get_positions())
    # print(okx.get_positions_history())
    # print(okx.get_trade_fills_history(instType="SPOT"))
    # print(okx.get_orders_history_archive(instType="SPOT"))
    print(okx.get_order(instId="BTC-USDT", ordId="680800019749904384"))

