import json
from typing import List, Optional, Dict
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pydantic import BaseModel
from _utils.utils import *

class OKXResponse:
    def __init__(self, response: dict):
        self.code = response.get('code')
        self.msg = response.get('msg')
        self.data = response.get('data')

    def __repr__(self):
        return f"OKXResponse(code={self.code}, msg={self.msg}, data={self.data})"


from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base


Base = declarative_base()


@dataclass_json
@dataclass
class LinkedAlgoOrd:
    algoId: str


@dataclass_json
@dataclass
class OrderDetailDB(Base):
    __tablename__ = 'order_detail'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    acc_fill_sz = Column(String, comment='成交数量')
    algo_cl_ord_id = Column(String, comment='算法客户端订单ID')
    algo_id = Column(String, comment='算法ID')
    attach_algo_cl_ord_id = Column(String, comment='附加算法客户端订单ID')
    attach_algo_ords = Column(String, comment='附加算法订单列表')
    avg_px = Column(String, comment='平均价格')
    c_time = Column(String, comment='创建时间')
    cancel_source = Column(String, comment='取消来源')
    cancel_source_reason = Column(String, comment='取消原因')
    category = Column(String, comment='订单类型')
    ccy = Column(String, comment='货币')
    cl_ord_id = Column(String, comment='客户端订单ID')
    fee = Column(String, comment='手续费')
    fee_ccy = Column(String, comment='手续费货币')
    fill_px = Column(String, comment='成交价格')
    fill_sz = Column(String, comment='成交数量')
    fill_time = Column(String, comment='成交时间')
    inst_id = Column(String, comment='产品ID')
    inst_type = Column(String, comment='产品类型')
    is_tp_limit = Column(String, comment='是否止盈限价')
    lever = Column(String, comment='杠杆倍数')
    linked_algo_ord = Column(String, comment='关联算法订单ID')
    ord_id = Column(String, comment='订单ID')
    ord_type = Column(String, comment='订单类型')
    pnl = Column(String, comment='盈亏')
    pos_side = Column(String, comment='持仓方向')
    px = Column(String, comment='价格')
    px_type = Column(String, comment='价格类型')
    px_usd = Column(String, comment='美元价格')
    px_vol = Column(String, comment='价格波动')
    quick_mgn_type = Column(String, comment='快速保证金类型')
    rebate = Column(String, comment='返佣')
    rebate_ccy = Column(String, comment='返佣货币')
    reduce_only = Column(String, comment='仅减仓')
    side = Column(String, comment='买卖方向')
    sl_ord_px = Column(String, comment='止损价格')
    sl_trigger_px = Column(String, comment='止损触发价格')
    sl_trigger_px_type = Column(String, comment='止损触发价格类型')
    source = Column(String, comment='来源')
    state = Column(String, comment='状态')
    stp_id = Column(String, comment='止损单ID')
    stp_mode = Column(String, comment='止损模式')
    sz = Column(String, comment='订单数量')
    tag = Column(String, comment='标签')
    td_mode = Column(String, comment='交易模式')
    tgt_ccy = Column(String, comment='目标货币')
    tp_ord_px = Column(String, comment='止盈订单价格')
    tp_trigger_px = Column(String, comment='止盈触发价格')
    tp_trigger_px_type = Column(String, comment='止盈触发价格类型')
    trade_id = Column(String, comment='交易ID')
    u_time = Column(String, comment='更新时间')

    def __init__(self, **kwargs):
        # 转换 JSON 字符串为字典
        if 'attach_algo_ords' in kwargs:
            kwargs['attach_algo_ords'] = json.dumps(kwargs['attach_algo_ords'])
        if 'linked_algo_ord' in kwargs:
            kwargs['linked_algo_ord'] = json.dumps(kwargs['linked_algo_ord'])
        super().__init__(**kwargs)


def dict_to_order_detail(db_model_class, data_dict):
    """Convert a dictionary to an instance of a SQLAlchemy model class."""
    return db_model_class(**data_dict)


if __name__ == '__main__':
    # Example usage:
    response_data = '''
    {
        'data': [
            {
                'accFillSz': '0.297899',
                'algoClOrdId': '',
                'algoId': '',
                'attachAlgoClOrdId': '',
                'attachAlgoOrds': [],
                'avgPx': '3187.52',
                'cTime': '1721885808099',
                'cancelSource': '',
                'cancelSourceReason': '',
                'category': 'normal',
                'ccy': '',
                'clOrdId': '',
                'fee': '-0.000297899',
                'feeCcy': 'ETH',
                'fillPx': '3187.52',
                'fillSz': '0.297899',
                'fillTime': '1721885808101',
                'instId': 'ETH-USDT',
                'instType': 'SPOT',
                'isTpLimit': 'false',
                'lever': '',
                'linkedAlgoOrd': {'algoId': ''},
                'ordId': '1657032209015750656',
                'ordType': 'market',
                'pnl': '0',
                'posSide': '',
                'px': '',
                'pxType': '',
                'pxUsd': '',
                'pxVol': '',
                'quickMgnType': '',
                'rebate': '0',
                'rebateCcy': 'USDT',
                'reduceOnly': 'false',
                'side': 'buy',
                'slOrdPx': '',
                'slTriggerPx': '',
                'slTriggerPxType': '',
                'source': '',
                'state': 'filled',
                'stpId': '',
                'stpMode': 'cancel_maker',
                'sz': '949.56',
                'tag': '',
                'tdMode': 'cash',
                'tgtCcy': 'quote_ccy',
                'tpOrdPx': '',
                'tpTriggerPx': '',
                'tpTriggerPxType': '',
                'tradeId': '430393910',
                'uTime': '1721885808102'
            },
            {
                'accFillSz': '195.334',
                'algoClOrdId': '',
                'algoId': '',
                'attachAlgoClOrdId': '',
                'attachAlgoOrds': [],
                'avgPx': '2.855',
                'cTime': '1721309432026',
                'cancelSource': '',
                'cancelSourceReason': '',
                'category': 'normal',
                'ccy': '',
                'clOrdId': '',
                'fee': '-0.195334',
                'feeCcy': 'WLD',
                'fillPx': '2.855',
                'fillSz': '21.732',
                'fillTime': '1721309432027',
                'instId': 'WLD-USDT',
                'instType': 'SPOT',
                'isTpLimit': 'false',
                'lever': '',
                'linkedAlgoOrd': {'algoId': ''},
                'ordId': '1637692237267853312',
                'ordType': 'market',
                'pnl': '0',
                'posSide': '',
                'px': '',
                'pxType': '',
                'pxUsd': '',
                'pxVol': '',
                'quickMgnType': '',
                'rebate': '0',
                'rebateCcy': 'USDT',
                'reduceOnly': 'false',
                'side': 'buy',
                'slOrdPx': '',
                'slTriggerPx': '',
                'slTriggerPxType': '',
                'source': '',
                'state': 'filled',
                'stpId': '',
                'stpMode': 'cancel_maker',
                'sz': '557.679',
                'tag': '',
                'tdMode': 'cash',
                'tgtCcy': 'quote_ccy',
                'tpOrdPx': '',
                'tpTriggerPx': '',
                'tpTriggerPxType': '',
                'tradeId': '30465982',
                'uTime': '1721309432029'
            }
        ]
    }
    '''



