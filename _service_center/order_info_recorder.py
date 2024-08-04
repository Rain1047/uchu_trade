import okx.SpreadTrading as SpreadTrading
import okx.Account as Account

from _data_center.data_object.enum_obj import EnumTradeType
from _utils.utils import *

config = ConfigUtils.get_config()


def get_order_info():
    print(config["apikey_demo"])

    flag = "1"  # 实盘:0 , 模拟盘:1
    if flag == EnumTradeType.PRODUCT.value:
        spreadAPI = SpreadTrading.SpreadTradingAPI(config["apikey"], config["secretkey"], config["passphrase"],
                                                   False, flag)
    if flag == EnumTradeType.DEMO.value:
        spreadAPI = SpreadTrading.SpreadTradingAPI(config["apikey_demo"], config["secretkey_demo"], config["passphrase"],
                                                   False, flag)
        result1 = spreadAPI.get_active_orders()
        print(result1)

        accountAPI = Account.AccountAPI(config["apikey_demo"], config["secretkey_demo"], config["passphrase"], False,
                                        flag)

        # 查看持仓信息
        result2 = accountAPI.get_positions()
        print(result2)

        result3 = accountAPI.get_positions_history()
        print(result3)
    print(config["apikey"])


if __name__ == '__main__':
    get_order_info()
