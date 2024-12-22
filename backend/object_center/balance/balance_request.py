from pydantic import BaseModel


class UpdateAccountBalanceSwitchRequest(BaseModel):
    ccy: str
    type: str
    switch: str
