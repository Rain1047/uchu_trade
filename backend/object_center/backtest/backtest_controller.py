import json

from fastapi import APIRouter, HTTPException
import logging

from backend.object_center.backtest.backtest_service import *

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/list_backtest_record")
def list_backtest_record(key: str):
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
def run_backtest(strategy_id: int):
    try:
        run_result = BacktestService.run_backtest(strategy_id)
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
    result = list_key(symbol='BTC-USDT', strategy_id=8)
    print(result)
