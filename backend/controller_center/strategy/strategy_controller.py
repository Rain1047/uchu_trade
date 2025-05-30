from fastapi import APIRouter, HTTPException
import logging

from backend.controller_center.strategy.strategy_request import StrategyCreateOrUpdateRequest
from backend.controller_center.strategy.strategy_service import StrategyService

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
    print(f"Strategy created: {result['data']}")
    return result


@router.get("/list_strategy")
async def list_strategy(page_num: int = 1, page_size: int = 10):
    result = StrategyService.list_strategies(page_num, page_size)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    print(f"Strategies listed: {result}")
    return result


@router.put("/update_strategy/{strategy_id}")
async def update_strategy(strategy_id: int, request: StrategyCreateOrUpdateRequest):
    result = StrategyService.update_strategy(strategy_id, request)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.delete("/delete_strategy/{strategy_id}")
async def delete_strategy(strategy_id: int):
    result = StrategyService.delete_strategy(strategy_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.put("/toggle_strategy/{strategy_id}")
async def toggle_strategy(strategy_id: int, active: bool):
    result = StrategyService.toggle_strategy_status(strategy_id, active)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/get_strategy_config")
async def get_strategy_config():
    return {
        "success": True,
        "data": StrategyService.get_strategy_config()
    }


if __name__ == '__main__':
    # result = StrategyService.list_strategies(1, 10)
    print({
        "success": True,
        "data": StrategyService.get_strategy_config()
    })
