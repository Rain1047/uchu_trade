import okx.Trade as Trade
from backend._data_center.data_object.req.post_order_req import PostOrderReq
from backend._service.utils import *


# database port : 5432 password : rain
class TradeAPI:
    def __init__(self):
        self.okx_instance = None

    # 获取okx账号-模拟盘
    def get_okx_trade_demo(self):
        production = "0"
        demo = "1"
        if self.okx_instance is None:
            config = ConfigUtils.get_config()
            self.okx_instance = Trade.TradeAPI(config['apikey_demo'], config['secretkey_demo'], config['passphrase'],
                                               False,
                                               demo)
            print("new trade instance created.")
        return self.okx_instance

    # 获取okx账号-实盘
    def get_okx_trade_real(self):
        production = "0"
        if self.okx_instance is None:
            config = ConfigUtils.get_config()
            self.okx_instance = Trade.TradeAPI(config['apikey'], config['secretkey'], config['passphrase'],
                                               False, production)
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
        headers = {'Content-Type': 'application/json', 'OK-ACCESS-SIGN': str(0), 'OK-ACCESS-TIMESTAMP': str(0)}
        okx = self.get_okx_trade_demo()
        try:
            result = okx.place_order(
                instId=order_instance.instId,
                tdMode=order_instance.tdMode,
                clOrdId=order_instance.clOrdId,
                side=order_instance.side,
                ordType=order_instance.ordType,
                px=order_instance.px,
                sz=order_instance.sz
            )
            print("trade res: {}".format(result))
            return result
        except Exception as order_exception:
            print(f"Error placing order: {order_exception}")
            return {"status": "error", "error_message": str(order_exception)}

    # 下单-策略下单
    def post_order_algo(self, order_instance: PostOrderReq):
        # params = {'instId': instId, 'tdMode': tdMode, 'side': side, 'ordType': ordType, 'sz': sz, 'ccy': ccy,
        #           'posSide': posSide, 'reduceOnly': reduceOnly, 'tpTriggerPx': tpTriggerPx, 'tpOrdPx': tpOrdPx,
        #           'slTriggerPx': slTriggerPx, 'slOrdPx': slOrdPx, 'triggerPx': triggerPx, 'orderPx': orderPx,
        #           'tgtCcy': tgtCcy, 'pxVar': pxVar, 'szLimit': szLimit, 'pxLimit': pxLimit,
        #           'timeInterval': timeInterval,
        #           'pxSpread': pxSpread, 'tpTriggerPxType': tpTriggerPxType, 'slTriggerPxType': slTriggerPxType,
        #           'callbackRatio': callbackRatio, 'callbackSpread': callbackSpread, 'activePx': activePx,
        #           'tag': tag, 'triggerPxType': triggerPxType, 'closeFraction': closeFraction,
        #           'quickMgnType': quickMgnType, 'algoClOrdId': algoClOrdId}
        # if (order_instance.tradeType.__eq__("0")
        headers = {'Content-Type': 'application/json', 'OK-ACCESS-SIGN': str(0), 'OK-ACCESS-TIMESTAMP': str(0)}
        okx = self.get_okx_trade_demo()
        try:
            result = okx.place_algo_order(
                instId=order_instance.instId,
                tdMode=order_instance.tdMode,
                side=order_instance.side,
                ordType=order_instance.ordType,
                sz=order_instance.sz,
                slOrdPx=order_instance.slOrdPx,
                slTriggerPx=order_instance.slTriggerPx
            )
            print("trade res: {}".format(result))
            return result
        except Exception as order_exception:
            print(f"Error placing order: {order_exception}")
            return {"status": "error", "error_message": str(order_exception)}

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

    order_params_limit = {
        "instId": "BTC-USDT",
        "tdMode": "cash",
        "clOrdId": "b15",
        "side": "buy",
        "ordType": "limit",
        "px": "2.15",
        "sz": "2"
    }

    # 市价
    order_params_market = {
        "instId": "BTC-USDT",
        "tdMode": "cash",
        "side": "buy",
        "ordType": "market",
        "sz": "2",
        "px": ""
    }

    # 获取市价

    # 带止损
    order_params_algo = {
        "instId": "BTC-USDT",
        "tdMode": "cash",
        "side": "buy",
        "ordType": "conditional",
        "sz": "2",
        "px": ""
    }

    order_limit = PostOrderReq(**order_params_limit)
    order_market = PostOrderReq(**order_params_market)
    order_algo = PostOrderReq(**order_params_algo)
    #
    # try:
    #     trade = TradeAPI()
    #     trade_result = trade.post_order(order_limit)
    #     # print("trade res: {}".format(trade_result))
    # except Exception as e:
    #     print(f"Error: {e}")
    #
    # try:
    #     trade = TradeAPI()
    #     trade_result = trade.post_order(order_market)
    #     # print("trade res: {}".format(trade_result))
    # except Exception as e:
    #     print(f"Error: {e}")

    try:
        trade = TradeAPI()
        trade_result = trade.post_order(order_market)
        # print("trade res: {}".format(trade_result))
    except Exception as e:
        print(f"Error: {e}")
