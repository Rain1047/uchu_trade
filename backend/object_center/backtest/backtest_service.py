from backend.backtest_center.backtest_main import *
from backend.backtest_center.models.backtest_result import BacktestResults


class BacktestService:
    @staticmethod
    def list_backtest() -> dict:
        pass

    @staticmethod
    def run_backtest():
        result: BacktestResults = backtest_main()
