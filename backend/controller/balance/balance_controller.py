from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from backend.service.okx_service.balance import list_account_balance

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/list_balance")
def get_balance():
    try:
        balance_list = list_account_balance()
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
    get_balance()
