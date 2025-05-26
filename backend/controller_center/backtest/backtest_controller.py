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


@router.get("/list_strategies")
def list_strategies():
    try:
        strategies = BacktestService.list_strategies()
        return {
            "success": True,
            "data": strategies
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_key")
def list_key(strategy_id: int):
    try:
        key_list = BacktestService.list_key(str(strategy_id))
        return {
            "success": True,
            "data": key_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_record")
def list_record(key: str):
    try:
        records = BacktestService.list_record_by_key(key)
        return {
            "success": True,
            "data": records
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/get_backtest_detail")
def get_backtest_detail(key: str):
    try:
        detail = BacktestService.get_backtest_detail(key)
        return {
            "success": True,
            "data": detail
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/list_backtest_results")
def list_backtest_results(
    strategy_id: int = None,
    start_time: str = None,
    end_time: str = None,
    min_profit_rate: float = None,
    max_profit_rate: float = None,
    min_win_rate: float = None,
    max_win_rate: float = None,
    min_trades: int = None,
    max_trades: int = None
):
    try:
        results = BacktestService.list_backtest_results(
            strategy_id=strategy_id,
            start_time=start_time,
            end_time=end_time,
            min_profit_rate=min_profit_rate,
            max_profit_rate=max_profit_rate,
            min_win_rate=min_win_rate,
            max_win_rate=max_win_rate,
            min_trades=min_trades,
            max_trades=max_trades
        )
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/run_backtest")
def run_backtest(request: BackTestRunRequest):
    try:
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
