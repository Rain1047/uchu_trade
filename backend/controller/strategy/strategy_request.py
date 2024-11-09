from pydantic import BaseModel
from typing import Optional


class StrategyPageRequest(BaseModel):
    pageSize: int = 10
    pageNum: int = 1
    inst_id: str | None = None


class StrategyCreateOrUpdateRequest(BaseModel):
    name: str
