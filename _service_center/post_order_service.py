import okx.Trade as Trade
from _data_center.data_object.req.post_order_req import *
from _data_center.data_object.enum_obj import *
from _service_center.utils import *


# database port : 5432 password : rain
class TradeAPI:
    def __init__(self):
        self.okx_instance = None

    # 获取okx账号-模拟盘
    def get_okx_trade_demo(self):
        if self.okx_instance is None:
            config = ConfigUtils.get_config()
            self.okx_instance = Trade.TradeAPI(config['apikey_demo'], config['secretkey_demo'], config['passphrase'],
                                               False, "1")
            print("new trade instance created.")
        return self.okx_instance

    # 获取okx账号-实盘
    def get_okx_trade_product(self):
        if self.okx_instance is None:
            config = ConfigUtils.get_config()
            self.okx_instance = Trade.TradeAPI(config['apikey'], config['secretkey'], config['passphrase'],
                                               False, "0")
            print("new trade instance created.")
        return self.okx_instance

    # 下单
    def post_order(self, order_instance: PostOrderReq):
        # 判断order类型，当order类型为
        if order_instance.ordType in ["limit", "market"]:
            print("order_instance: {}".format(order_instance))
            return self.post_order_common(order_instance)
        elif order_instance.ordType in ["conditional", "oco", "trigger", "move_order_stop"]:
            return self.post_order_algo(order_instance)

    # 下单-普通
    def post_order_common(self, order_instance: PostOrderReq):
        if order_instance.tradeType.__eq__(EnumTradeType.DEMO.value):
            okx = self.get_okx_trade_demo()
        else:
            okx = self.get_okx_trade_product()

        try:
            result = okx.place_order(
                instId=order_instance.instId,
                tdMode=order_instance.tdMode,
                sz=order_instance.sz,
                side=order_instance.side,
                posSide=order_instance.posSide,
                ordType=order_instance.ordType,
                slTriggerPx=order_instance.slTriggerPx,
                slOrdPx=order_instance.slOrdPx,
                slTriggerPxType=order_instance.slTriggerPxType
            )
            return result
        except Exception as order_exception:
            print(f"Error placing order: {order_exception}")
            return {"status": "error", "error_message": str(order_exception)}

    # 下单-策略下单
    def post_order_algo(self, order_instance: PostOrderReq):
        okx = self.get_okx_trade_demo()
        try:
            result = okx.place_algo_order(
                instId=order_instance.instId,
                tdMode=order_instance.tdMode,
                sz=order_instance.sz,
                side=order_instance.side,
                posSide=order_instance.posSide,
                ordType=order_instance.ordType,
                slTriggerPx=order_instance.slTriggerPx,
                slOrdPx=order_instance.slOrdPx
            )
            print("trade res: {}".format(result))
            return result
        except Exception as order_exception:
            print(f"Error placing order: {order_exception}")
            return {"status": "error", "error_message": str(order_exception)}

    # 下单
    def get_order_info(self, type: str, instId: str, orderId: str):
        if type.__eq__(EnumTradeType.DEMO.value):
            okx = self.get_okx_trade_demo()
        else:
            okx = self.get_okx_trade_product()
        result_info = okx.get_order(
            instId=instId,
            ordId=orderId
        )
        return result_info

    # 提取 details 作为 DataFrame
    def details_to_dataframe(self):
        # 检查数据中是否包含 'data' 键和 'details' 键
        if 'data' in self and 'details' in self['data'][0]:
            # 提取 details 数据
            details = self['data'][0]['details']
            # 创建 DataFrame
            df = pd.DataFrame(details)
            return df
        else:
            return pd.DataFrame()  # 如果没有找到 details 键，返回空的 DataFrame


if __name__ == "__main__":
    # 现货下单
    order_params_limit = {
        "tradeType": EnumTradeType.PRODUCT.value,
        "instId": "BTC-USDT",
        "tdMode": "cash",
        "clOrdId": "b15",
        "side": "buy",
        "ordType": "limit",
        # 限价价格
        "px": "2.15",
        # 数量
        "sz": "2"
    }
    order_limit = PostOrderReq(**order_params_limit)

    # 合约下单
    swap_params = {
        "tradeType": EnumTradeType.DEMO.value,
        "instId": "BTC-USDT-SWAP",
        # 数量
        "sz": "73",
        # 逐仓
        "tdMode": "isolated",
        "side": EnumSide.BUY.value,
        "posSide": EnumPosSide.LONG.value,
        # 市价单
        "ordType": "market",
        # 止损触发价
        "slTriggerPx": "65000.0",
        # 止损委托价 -1时为市价
        "slOrdPx": "-1",
        "slTriggerPxType": "last"
    }
    swap_order = PostOrderReq(**swap_params)

    try:
        trade = TradeAPI()
        # trade_result = trade.post_order(order_limit)
        trade_result = trade.post_order(swap_order)
        print("trade res: {}".format(trade_result))
    except Exception as e:
        print(f"Error: {e}")
