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
            'int': self.id,
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

