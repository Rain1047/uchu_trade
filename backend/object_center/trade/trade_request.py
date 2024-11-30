from typing import Optional

from pydantic import BaseModel


class TradePageRequest(BaseModel):
    pageSize: int = 10
    pageNum: int = 1
    inst_id: str | None = None
    fill_start_time: str | None = None
    fill_end_time: str | None = None


class TradeResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
