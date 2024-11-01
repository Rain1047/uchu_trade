from typing import Optional

from pydantic import BaseModel


class PageRequest(BaseModel):
    # 分页参数
    pageSize: int = 10
    pageNum: int = 1
    inst_id: Optional[str] = ''
    fill_start_time: Optional[str] = ''
    fill_end_time: Optional[str] = ''
