from pydantic import BaseModel
from typing import Optional


class StrategyPageRequest(BaseModel):
    pageSize: int = 10
    pageNum: int = 1
    inst_id: str | None = None


class StrategyCreateOrUpdateRequest(BaseModel):
    id: int | None = None
    name: str
    trade_pair: str | None = None
    time_frame: str | None = None
    side: str | None = None
    entry_per_trans: float | None = None
    loss_per_trans: float | None = None
    entry_st_code: str | None = None
    exit_st_code: str | None = None
    filter_st_code: str | None = None
    stop_loss_config: dict | None = None
    schedule_config: dict | None = None


# {
#   "name": "策略实例名称",
#   "trade_pair": "交易对",
#   "time_frame": "时间窗",
#   "side": "交易方向",
#   "entry_per_trans": 0, # 每笔交易金额
#   "loss_per_trans": 0, # 每笔损失金额
#   "entry_st_code": "入场策略",
#   "exit_st_code": "离场策略",
#   "filter_st_code": "过滤策略",
#   "stop_loss_config": {"trailing_stop": "15", "stop_limit": "sma20"},
#   "schedule_config": {"date":"1,2,3,4","time":"0-10,21-23"}
# }