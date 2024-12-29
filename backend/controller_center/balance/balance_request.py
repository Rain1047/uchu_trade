from pydantic import BaseModel


class UpdateAccountBalanceSwitchRequest(BaseModel):
    ccy: str
    type: str
    switch: str


class TradeConfig(BaseModel):
    ccy: str
    type: str
    indicator: str
    indicator_val: str
    percentage: str | None
    amount: str | None
    switch: str | None
    exec_nums: str | None
    target_price: str | None


