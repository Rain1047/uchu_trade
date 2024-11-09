from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from backend.controller.strategy.strategy_request import StrategyCreateOrUpdateRequest

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/create_strategy")
async def create_strategy_instance(request: StrategyCreateOrUpdateRequest):
    print(f"Received strategy request: {request}")


