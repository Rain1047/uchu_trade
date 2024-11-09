from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from backend.service.okx_service import get_fill_history  # 假设这是你的服务函数

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 定义模型
class PageRequest(BaseModel):
    pageSize: int = 10
    pageNum: int = 1
    inst_id: str | None = None
    fill_start_time: str | None = None
    fill_end_time: str | None = None


class TradeResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


# 路由处理
@router.post("/list_history")  # 注意这里使用 router 而不是 app
async def get_fills_history(request: PageRequest):
    try:
        print(f"Received trade request: {request}")

        page_result = get_fill_history(request)

        if page_result.get("success"):
            return page_result
        else:
            mock_data = {
                "items": [
                    {
                        "trade_id": "MOCK-001",
                        "inst_id": "BTC-USDT",
                        "side": "buy",
                        "fill_px": "42000.50",
                        "fill_sz": "0.1234",
                        "fee": "-0.000123",
                        "fill_time": "1699000000000"
                    }
                ],
                "total_count": 1,
                "page_size": request.pageSize,
                "page_num": request.pageNum
            }
            return TradeResponse(
                success=True,
                data=mock_data
            )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
