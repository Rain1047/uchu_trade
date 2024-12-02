import json

from fastapi import APIRouter, HTTPException
import logging

from backend.object_center.backtest.backtest_service import *

# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/list_backtest")
def list_backtest():
    try:
        backtest_list = BacktestService.list_backtest()
        return {
            "success": True,
            "data": backtest_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_key")
def list_key(strategy_id: int, symbol: str):
    try:
        result = BacktestService.list_key(str(strategy_id), symbol=symbol)
        for item in result:
            print(json.dumps(item))
        return {
            "success": True,
            "data": result
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