from fastapi import APIRouter, HTTPException
import logging

from backend.service_center.okx_service.okx_balance_service import OKXBalanceService

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/list_balance")
def get_balance_list():
    try:
        okx_balance_service = OKXBalanceService()
        balance_list = okx_balance_service.list_account_balance()
        return {
            "success": True,
            "data": balance_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


if __name__ == '__main__':
    get_balance_list()
