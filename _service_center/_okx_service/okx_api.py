import okx.Account as Account
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

    def _load_config(self):
        with open(self.config_file_path, 'r') as config_file:
            self.config = json.load(config_file)

    def _initialize_account_api(self):
        self.accountAPI = Account.AccountAPI(self.apikey, self.secretkey, self.passphrase, False, self.flag)

    def get_account_balance(self) -> json:
        result = self.accountAPI.get_account_balance()
        return result


# 示例用法
if __name__ == "__main__":
    okx = OKXAPIWrapper(env=EnumTradeEnv.MARKET.value)
    print(okx.get_account_balance())  # 验证初始化是否成功
