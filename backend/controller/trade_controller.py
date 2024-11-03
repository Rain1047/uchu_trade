from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.config.settings import Settings, get_settings
from backend.config.middleware import limiter
from backend.config.settings import settings
from backend.service.okx_service import *

router = APIRouter(prefix="/api/trades")


# Models
class TradeRequest(BaseModel):
    pageSize: int = 10
    pageNum: int = 1
    inst_id: Optional[str] = None
    fill_start_time: Optional[str] = None
    fill_end_time: Optional[str] = None


class TradeResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


# Routes
@router.post("/history", response_model=TradeResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_fills_history(request: PageRequest):
    try:
        page_result = get_fill_history(request)
        if page_result.is_success():
            items = page_result.get_items()
            total = page_result.get_total_count()
            print(f"Retrieved {len(items)} of {total} items")
            return items
        else:
            print(f"Error: {page_result.get_message()}")

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
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
