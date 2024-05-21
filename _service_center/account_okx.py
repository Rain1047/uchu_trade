import time
from requests.exceptions import SSLError
import okx.Account as Account
import pandas as pd
import json
import os

import psycopg2

from _utils.config_util import get_config


# database port : 5432 password : rain
class AccountAPI:

    def __init__(self):
        self.okx_instance = None

    # 获取okx账号
    def get_okx_account(self):
        if self.okx_instance is None:
            config = get_config()
            self.okx_instance = Account.AccountAPI(config['apikey'], config['secretkey'], config['passphrase'], False,
                                                   "0")
            print("new account instance created.")
        return self.okx_instance

    def get_balance(self):
        okx = self.get_okx_account()
        # Convert numeric parameters to strings in the headers
        headers = {'Content-Type': 'application/json', 'OK-ACCESS-SIGN': str(0), 'OK-ACCESS-TIMESTAMP': str(0)}
        account_balance = okx.get_account_balance()
        return account_balance

    def get_positions(self):
        okx = self.get_okx_account()
        # Convert numeric parameters to strings in the headers
        headers = {'Content-Type': 'application/json', 'OK-ACCESS-SIGN': str(0), 'OK-ACCESS-TIMESTAMP': str(0)}
        account_positions = okx.get_positions()
        return account_positions

    # def find_value_by_key(data, target_key):
    #     if isinstance(data, dict):
    #         for key, value in data.items():
    #             if key == target_key:
    #                 return value
    #             if isinstance(value, (dict, list)):
    #                 res = find_value_by_key(value, target_key)
    #                 if res is not None:
    #                     return res
    #     elif isinstance(data, list):
    #         for item in data:
    #             if isinstance(item, (dict, list)):
    #                 res = find_value_by_key(item, target_key)
    #                 if res is not None:
    #                     return res
    #     return None

    # 提取 details 作为 DataFrame
    def details_to_dataframe(json_data):
        # 检查数据中是否包含 'data' 键和 'details' 键
        if 'data' in json_data and 'details' in json_data['data'][0]:
            # 提取 details 数据
            details = json_data['data'][0]['details']
            # 创建 DataFrame
            df = pd.DataFrame(details)
            return df
        else:
            return pd.DataFrame()  # 如果没有找到 details 键，返回空的 DataFrame


if __name__ == "__main__":
    try:
        account = AccountAPI()
    except Exception as e:
        print(f"Error1: {e}")

    try:
        account_balance = account.get_balance()
        print(account_balance)

        time.sleep(2)

        # Uncomment the following lines if needed:
        # total_eq = find_value_by_key(account_balance, 'totalEq')
        # print(total_eq)

        # 使用函数并打印结果
        # df_details = details_to_dataframe(account_balance)
        # df_details

    except SSLError as e:
        print(f"SSL Error: {e}")
