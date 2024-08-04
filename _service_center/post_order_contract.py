
import okx.Account as Account
import json
import os

from _utils.utils import *


class AccountAPI:
    def __init__(self):
        self.okx_instance = None

    # 获取okx账号-模拟盘
    def get_okx_trade_demo(self):
        demo = "1"
        if self.okx_instance is None:
            config = ConfigUtils.get_config()
            self.okx_instance = Account.AccountAPI(config['apikey_demo'], config['secretkey_demo'], config['passphrase'],
                                               False, demo)
            print("new trade instance created.")
        return self.okx_instance

    # 获取okx账号-实盘
    def get_okx_trade_product(self):
        production = "0"
        if self.okx_instance is None:
            config = ConfigUtils.get_config()
            self.okx_instance = Account.AccountAPI(config['apikey'], config['secretkey'], config['passphrase'],
                                               False, production)
            print("new trade instance created.")
        return self.okx_instance

    # 合约交易
    def post_order_contract(self):
        # 在逐仓交易模式下，设置币币杠杆的杠杆倍数（币对层面）
        acc = self.get_okx_trade_demo()
        result = acc.set_leverage(
            instId="BTC-USDT",
            lever="5",
            mgnMode="isolated"
        )
