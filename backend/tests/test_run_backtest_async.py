import asyncio
import logging
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.backtest_center.models import BacktestConfig
from backend.controller_center.backtest.enhanced_backtest_controller import run_backtest_async

logging.basicConfig(level=logging.INFO)

PAYLOAD = {
    "entry_strategy": "dbb_entry_long_strategy",
    "exit_strategy": "dbb_exit_long_strategy",
    # "filter_strategy": "sma_perfect_order_filter_strategy",
    "symbols": ["BTC"],
    "timeframe": "1d",
    "backtest_period": "3m",
    "initial_cash": 100000,
    "risk_percent": 2,
    "commission": 0.001,
    "description": "本地异步回测单元测试"
}


def build_config(data: dict) -> BacktestConfig:
    return BacktestConfig(
        entry_strategy=data["entry_strategy"],
        exit_strategy=data["exit_strategy"],
        filter_strategy=data.get("filter_strategy"),
        symbols=data["symbols"],
        timeframe=data["timeframe"],
        backtest_period=data["backtest_period"],
        initial_cash=data["initial_cash"],
        risk_percent=data["risk_percent"],
        commission=data["commission"],
        description=data.get("description", "测试回测"),
        created_at=datetime.now()
    )


async def main():
    config = build_config(PAYLOAD)
    # 999 作测试记录 ID
    await run_backtest_async(config, record_id=999)


if __name__ == "__main__":
    asyncio.run(main()) 