from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Body, Query
import logging

from backend.controller_center.balance.balance_request import TradeConfig, UpdateAccountBalanceSwitchRequest, \
    TradeConfigExecuteHistory, ConfigUpdateRequest
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


@router.post("/update_account_balance_config_switch")
def update_config_switch(request: UpdateAccountBalanceSwitchRequest):
    try:
        balance_service = BalanceService()
        result = balance_service.update_account_balance_switch(request)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/save_config")
def save_config(config_update_request: ConfigUpdateRequest):
    try:
        config_list = config_update_request.config_list
        config_list = [config.to_dict() for config in config_list]
        print(config_list)
        balance_service = BalanceService()
        result = balance_service.batch_create_or_update_balance_configs(config_list,
                                                                        config_type=config_update_request.type)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_balance_configs")
async def list_balance_configs(
        ccy: str = Query(..., description="币种"),
        config_type: str = Query(..., description="配置类型: stop_loss 或 limit_order"),
):
    try:
        balance_service = BalanceService()
        configs = balance_service.list_trade_configs(ccy, config_type)
        return {
            "success": True,
            "data": configs
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


@router.post("/list_config_execute_records")
def list_config_execute_records(config_execute_history_request: TradeConfigExecuteHistory):
    try:
        balance_service = BalanceService()
        configs = balance_service.list_config_execute_records(config_execute_history_request)
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
