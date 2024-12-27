from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Body
import logging

from backend.controller_center.balance.balance_request import TradeConfig
from backend.controller_center.balance.balance_service import BalanceService
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService

# 创建路由器实例

router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/list_balance")
def get_balance_list():
    try:
        balance_service = BalanceService()
        balance_list = balance_service.list_account_balance()
        # print({
        #     "success": True,
        #     "data": balance_list
        # })
        return {
            "success": True,
            "data": balance_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/save_config")
def save_config(config_list: List[TradeConfig]):
    try:
        config_list = [config.dict() for config in config_list]
        balance_service = BalanceService()
        result = balance_service.save_update_balance_config(config_list)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_configs/{ccy}/{type}")
def list_configs(ccy: str, type_: str):
    try:
        balance_service = BalanceService()
        configs = balance_service.list_trade_configs(ccy, type_)
        return {
            "success": True,
            "data": configs
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


if __name__ == '__main__':
    get_balance_list()
