from datetime import datetime
from typing import List

from pydantic import BaseModel


class UpdateAccountBalanceSwitchRequest(BaseModel):
    ccy: str
    type: str
    switch: str


class TradeConfig(BaseModel):
    id: int | None
    ccy: str
    type: str
    indicator: str
    indicator_val: str
    percentage: str | None
    amount: str | None
    switch: str | None
    exec_nums: str | None
    target_price: str | None

    def to_dict(self):
        return {
            'id': self.id,
            'ccy': self.ccy,
            'type': self.type,
            'indicator': self.indicator,
            'indicator_val': self.indicator_val,
            'target_price': self.target_price,
            'percentage': self.percentage,
            'amount': self.amount,
            'switch': self.switch,
            'exec_nums': self.exec_nums,
            'is_del': '0'
        }


class TradeRecordPageRequest(BaseModel):
    # 交易符号
    ccy: str
    # 交易类别
    type: str
    # 交易方向
    side: str
    # 交易状态
    status: str
    # 交易方式
    exec_source: str

    # 开始/结束时间
    begin_time: datetime
    end_time: datetime

    def to_dict(self):
        return {
            'ccy': self.ccy,
            'type': self.type,
            'side': self.side,
            'status': self.status,
            'exec_source': self.exec_source,
            'begin_time': self.begin_time,
            'end_time': self.end_time
        }


class ConfigUpdateRequest(BaseModel):
    config_list: List[TradeConfig]
    type: str
