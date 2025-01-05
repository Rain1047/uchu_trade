from fastapi import APIRouter, HTTPException

from backend.controller_center.balance.balance_request import TradeRecordPageRequest
from backend.controller_center.record.record_service import RecordService
from backend.controller_center.trade.trade_service import *

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/list_spot_record")
def list_spot_record(request: TradeRecordPageRequest):
    try:
        print(f"Received trade request: {request}")

        page_result = RecordService.list_config_execute_records(request)
        page_result['success'] = True
        return page_result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == '__main__':
    request = TradeRecordPageRequest()
    request.ccy = "ETH"
    print(list_spot_record(request))
