from fastapi import APIRouter, HTTPException
import logging

from backend.controller_center.balance.balance_request import TradeRecordPageRequest
from backend.controller_center.record.record_service import RecordService
from backend.service_center.okx_service.okx_spot_order_record_service import SpotOrderRecordService
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend._utils import LogConfig

# 创建路由器实例
router = APIRouter()

# 设置日志
logger = LogConfig.get_logger(__name__)


@router.post("/list_spot_record")
def list_spot_record(request: TradeRecordPageRequest):
    try:
        logger.info(f"Received trade request: {request}")
        
        # 初始化服务
        okx = OKXAPIWrapper()
        spot_order_record_service = SpotOrderRecordService(okx.trade_api, RecordService())
        
        # 更新现货订单记录
        logger.info("开始更新现货订单记录")
        spot_order_record_service.save_update_spot_order_record()
        logger.info("现货订单记录更新完成")

        # 获取分页数据
        page_result = RecordService.list_config_execute_records(request)
        page_result['success'] = True
        return page_result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == '__main__':
    request = TradeRecordPageRequest()
    request.ccy = "ETH"
    print(list_spot_record(request))
