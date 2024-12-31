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


class TradeConfigExecuteHistory(BaseModel):
    ccy: str
    type: str
    status: str
    create_time: str
    exec_source: str

    def to_dict(self):
        return {
            'ccy': self.ccy,
            'type': self.type,
            'exec_source': self.exec_source,
            'status': self.status,
            'create_time': self.create_time
        }


class ConfigUpdateRequest(BaseModel):
    config_list: List[TradeConfig]
    type: str
