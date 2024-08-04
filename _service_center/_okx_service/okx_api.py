import okx.Account as Account
import okx.Trade as Trade
import json
from typing import Optional, Dict, Type

from _data_center.data_object.dao.order_detail import OrderDetailDB
from _data_center.data_object.enum_obj import *
from _utils.utils import DatabaseUtils


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

        self._initialized = True
        print("{} OKX API initialized.".format(self.env))

    def _load_config(self):
        with open(self.config_file_path, 'r') as config_file:
            self.config = json.load(config_file)

    def _initialize_account_api(self):
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
    def get_orders_history_archive(self, instType: Optional[str] = EnumInstanceType.SPOT.value, **kwargs) -> json:
        # 查询币币历史订单（3月内）
        return self.tradeAPI.get_orders_history_archive(instType=instType, **kwargs)

    # 获取订单信息
    def get_order(self, instId: str, ordId: str) -> json:
        return self.tradeAPI.get_order(instId=instId, ordId=ordId)

    # 存储数据到数据库
    def insert_order_details(self, api_response: Dict, db_model_class: Type):
        session = DatabaseUtils.get_db_session()
        data = api_response.get('data', [])
        for order_detail_dict in data:
            # Convert dictionary to db_model_class instance
            order_detail_instance = dict_to_order_detail(db_model_class, order_detail_dict)
            # Add instance to the session
            session.add(order_detail_instance)
        # Commit the transaction
        session.commit()


def store_data_to_db(json_data: str):
    if not isinstance(json_data, str):
        raise ValueError("JSON 数据应该是字符串类型")

    data = json.loads(json_data)
    order_details = data.get('data', [])

    if not order_details:
        print("没有订单数据需要保存.")
        return

    db_utils = DatabaseUtils()
    session = db_utils.get_db_session()

    try:
        for item in order_details:
            db_instance = OrderDetailDB(
                acc_fill_sz=item.get('accFillSz'),
                algo_cl_ord_id=item.get('algoClOrdId'),
                algo_id=item.get('algoId'),
                attach_algo_cl_ord_id=item.get('attachAlgoClOrdId'),
                # attach_algo_ords=json.dumps(item.get('attachAlgoOrds')),  # Convert list to JSON string
                avg_px=item.get('avgPx'),
                c_time=item.get('cTime'),
                cancel_source=item.get('cancelSource'),
                cancel_source_reason=item.get('cancelSourceReason'),
                category=item.get('category'),
                ccy=item.get('ccy'),
                cl_ord_id=item.get('clOrdId'),
                fee=item.get('fee'),
                fee_ccy=item.get('feeCcy'),
                fill_px=item.get('fillPx'),
                fill_sz=item.get('fillSz'),
                fill_time=item.get('fillTime'),
                inst_id=item.get('instId'),
                inst_type=item.get('instType'),
                is_tp_limit=item.get('isTpLimit'),
                lever=item.get('lever'),
                # linked_algo_ord=json.dumps(item.get('linkedAlgoOrd')),  # Convert dict to JSON string
                ord_id=item.get('ordId'),
                ord_type=item.get('ordType'),
                pnl=item.get('pnl'),
                pos_side=item.get('posSide'),
                px=item.get('px'),
                px_type=item.get('pxType'),
                px_usd=item.get('pxUsd'),
                px_vol=item.get('pxVol'),
                quick_mgn_type=item.get('quickMgnType'),
                rebate=item.get('rebate'),
                rebate_ccy=item.get('rebateCcy'),
                reduce_only=item.get('reduceOnly'),
                side=item.get('side'),
                sl_ord_px=item.get('slOrdPx'),
                sl_trigger_px=item.get('slTriggerPx'),
                sl_trigger_px_type=item.get('slTriggerPxType'),
                source=item.get('source'),
                state=item.get('state'),
                stp_id=item.get('stpId'),
                stp_mode=item.get('stpMode'),
                sz=item.get('sz'),
                tag=item.get('tag'),
                td_mode=item.get('tdMode'),
                tgt_ccy=item.get('tgtCcy'),
                tp_ord_px=item.get('tpOrdPx'),
                tp_trigger_px=item.get('tpTriggerPx'),
                tp_trigger_px_type=item.get('tpTriggerPxType'),
                trade_id=item.get('tradeId'),
                u_time=item.get('uTime')
            )
            session.add(db_instance)

        session.commit()
        print("数据已成功存储到数据库.")
    except Exception as e:
        session.rollback()
        print(f"存储数据时出错: {e}")
    finally:
        session.close()


def dict_to_order_detail(model_class, data_dict):
    # 创建模型实例
    instance = model_class()

    for key, value in data_dict.items():
        # 将 camelCase 键转换为 snake_case
        snake_case_key = to_snake_case(key)

        # 处理嵌套的字典，比如 linkedAlgoOrd
        if isinstance(value, dict):
            # 将嵌套字典展开到父字典中
            for nested_key, nested_value in value.items():
                nested_snake_key = f"{snake_case_key}_{to_snake_case(nested_key)}"
                setattr(instance, nested_snake_key, convert_value(nested_value))
        else:
            # 设置实例的属性
            if hasattr(instance, snake_case_key):
                setattr(instance, snake_case_key, convert_value(value))
            else:
                print(f"警告: {snake_case_key} 不是 {model_class.__name__} 的属性")

    return instance


def to_snake_case(camel_case_str):
    # 将 camelCase 转换为 snake_case
    return ''.join(['_' + i.lower() if i.isupper() else i for i in camel_case_str]).lstrip('_')


def convert_value(value):
    # 将非字符串类型转换为字符串
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


# Sample function to insert data into the database
def insert_order_details(api_response, db_model_class):
    session = DatabaseUtils.get_db_session()
    data = api_response.get('data', [])
    for order_detail_dict in data:
        # Convert dictionary to db_model_class instance
        order_detail_instance = dict_to_order_detail(db_model_class, order_detail_dict)
        # Add instance to the session
        session.add(order_detail_instance)
    # Commit the transaction
    session.commit()


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
    insert_order_details(okx.get_orders_history_archive(), OrderDetailDB)
    # try:
    #     store_data_to_db(okx.get_orders_history_archive())
    #     print("Data stored successfully.")
    # except Exception as e:
    #     print(f"Error storing data: {e}")
    # finally:
    #     print("Done.")
    # print(okx.get_order(instId="BTC-USDT", ordId="680800019749904384"))
