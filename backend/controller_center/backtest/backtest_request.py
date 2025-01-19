from pydantic import BaseModel


class BackTestRunRequest(BaseModel):
    strategy_id: int
