from fastapi import APIRouter, HTTPException, Query
import logging
from datetime import datetime, timedelta
import asyncio
from typing import Optional

from backend.controller_center.balance.balance_request import TradeRecordPageRequest
from backend.controller_center.record.record_service import RecordService
from backend.service_center.okx_service.okx_spot_order_record_service import SpotOrderRecordService
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend._utils import LogConfig

# 创建路由器实例
router = APIRouter()

# 设置日志
logger = LogConfig.get_logger(__name__)

# 全局变量用于缓存上次更新时间
_last_update_time = None
_update_interval = timedelta(minutes=5)  # 5分钟内不重复更新


@router.post("/list_spot_record")
def list_spot_record(request: TradeRecordPageRequest, force_update: Optional[bool] = Query(False, description="是否强制更新OKX数据")):
    try:
        logger.info(f"Received trade request: {request}, force_update: {force_update}")
        
        global _last_update_time
        current_time = datetime.now()
        
        # 检查是否需要更新数据
        should_update = (
            force_update or 
            _last_update_time is None or 
            (current_time - _last_update_time) > _update_interval
        )
        
        if should_update:
            # 初始化服务
            okx = OKXAPIWrapper()
            spot_order_record_service = SpotOrderRecordService(okx.trade_api, RecordService())
            
            # 更新现货订单记录
            logger.info("开始更新现货订单记录")
            spot_order_record_service.save_update_spot_order_record()
            logger.info("现货订单记录更新完成")
            _last_update_time = current_time
        else:
            logger.info(f"跳过数据更新，距离上次更新仅过去 {(current_time - _last_update_time).total_seconds():.1f} 秒")

        # 获取分页数据
        page_result = RecordService.list_config_execute_records(request)
        page_result['success'] = True
        page_result['last_update'] = _last_update_time.isoformat() if _last_update_time else None
        page_result['data_freshness'] = 'updated' if should_update else 'cached'
        return page_result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/list_spot_record_fast")
def list_spot_record_fast(request: TradeRecordPageRequest):
    """
    快速查询接口，不更新OKX数据，直接返回数据库中的记录
    """
    try:
        logger.info(f"Received fast trade request: {request}")
        
        # 直接获取分页数据，不更新OKX数据
        page_result = RecordService.list_config_execute_records(request)
        page_result['success'] = True
        page_result['data_freshness'] = 'cache_only'
        return page_result
    except Exception as e:
        logger.error(f"Error processing fast request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/refresh_spot_record")
def refresh_spot_record():
    """
    手动刷新OKX数据接口
    """
    try:
        logger.info("手动刷新现货订单记录")
        
        # 初始化服务
        okx = OKXAPIWrapper()
        spot_order_record_service = SpotOrderRecordService(okx.trade_api, RecordService())
        
        # 更新现货订单记录
        spot_order_record_service.save_update_spot_order_record()
        
        global _last_update_time
        _last_update_time = datetime.now()
        
        logger.info("手动刷新完成")
        return {
            "success": True,
            "message": "数据刷新成功",
            "last_update": _last_update_time.isoformat()
        }
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == '__main__':
    request = TradeRecordPageRequest()
    request.ccy = "ETH"
    print(list_spot_record(request))
