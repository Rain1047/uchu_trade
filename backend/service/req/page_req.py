from typing import Optional

from pydantic import BaseModel


class PageRequest(BaseModel):
    # 分页参数
    pageSize: int = 10
    pageNum: int = 1
    inst_id: str | None = None
    fill_start_time: str | None = None
    fill_end_time: str | None = None
