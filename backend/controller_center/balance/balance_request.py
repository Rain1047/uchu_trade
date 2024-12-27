from pydantic import BaseModel


class UpdateAccountBalanceSwitchRequest(BaseModel):
    ccy: str
    type: str
    switch: str


class TradeConfig(BaseModel):
    type: str
    indicator: str
    interval: str
    percentage: str | None
    amount: str | None
    ccy: str
