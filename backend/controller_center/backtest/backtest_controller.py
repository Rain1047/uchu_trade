import json

from fastapi import APIRouter
import logging

from backend.controller_center.backtest.backtest_request import BackTestRunRequest
from backend.controller_center.backtest.backtest_service import *

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/list_symbol")
def list_symbol():
    try:
        symbols = BacktestService.list_symbol()
        return {
            "success": True,
            "data": symbols
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get('/list_strategy_by_symbol')
def list_strategy_by_symbol(symbol: str):
    try:
        strategy_list = BacktestService.list_strategy_by_symbol(symbol=symbol)
        return {
            "success": True,
            "data": strategy_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_record_by_key")
def list_record_by_key(key: str):
    try:
        record_list = BacktestService.list_record_by_key(key)
        return {
            "success": True,
            "data": record_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/get_backtest_detail")
def get_backtest_detail(key: str):
    try:
        record_list = BacktestService.get_backtest_detail(key)
        return {
            "success": True,
            "data": record_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_key")
def list_key(strategy_id: int, symbol: str):
    try:
        key_list = BacktestService.list_key(str(strategy_id), symbol=symbol)
        for item in key_list:
            print(json.dumps(item))
        return {
            "success": True,
            "data": key_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/run_backtest")
def run_backtest(request: BackTestRunRequest):
    try:
        print(request.strategy_id)
        run_result = BacktestService.run_backtest(request.strategy_id)
        return {
            "success": True,
            "data": run_result
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


if __name__ == '__main__':
    # list_backtest()
    result = run_backtest(strategy_id=8)
    print(result)
