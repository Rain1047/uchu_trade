import okx.SpreadTrading as SpreadTrading
import os
import json
import okx.Account as Account

script_dir = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.path.join(script_dir, '../config.json')
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)


def get_order_info():
    flag = "1"  # 实盘:0 , 模拟盘:1
    if flag == EnumTradeType.PRODUCT.value:
        spreadAPI = SpreadTrading.SpreadTradingAPI(config["apikey"], config["secretkey"], config["passphrase"],
                                                   False, flag)
    if flag == EnumTradeType.DEMO.value:
        spreadAPI = SpreadTrading.SpreadTradingAPI(config["apikeydemo"], config["secretkeydemo"], config["passphrase"],
                                                   False, flag)
        result1 = spreadAPI.get_active_orders()
        print(result1)

        accountAPI = Account.AccountAPI(config["apikeydemo"], config["secretkeydemo"], config["passphrase"], False,
                                        flag)

        # 查看持仓信息
        result2 = accountAPI.get_positions()
        print(result2)

        result3 = accountAPI.get_positions_history()
        print(result3)
    print(config["apikey"])
    # 获取订单详情
    # res = spreadAPI.get_order_details(ordId='691741894593933312')

    # res = spreadAPI.get_order_details(ordId='1905309079888199680')


if __name__ == '__main__':
    get_order_info()
