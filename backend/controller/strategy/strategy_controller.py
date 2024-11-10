from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from backend.controller.strategy.strategy_request import StrategyCreateOrUpdateRequest
from backend.controller.strategy.strategy_service import StrategyService

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/create_strategy")
async def create_strategy_instance(request: StrategyCreateOrUpdateRequest):
    print(f"Received strategy request: {request}")
    result = StrategyService.create_strategy(request)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/list_strategy")
async def list_strategy(page_num: int = 1, page_size: int = 10):
    result = StrategyService.list_strategies(page_num, page_size)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
