from backend.backtest_center.backtest_main import *
from backend.backtest_center.models.backtest_result import BacktestResults
from backend.object_center.object_dao.backtest_result import BacktestResult


class BacktestService:
    @staticmethod
    def list_backtest() -> dict:
        pass

    @staticmethod
    def list_key(strategy_id: str, symbol: str):
        return BacktestResult.list_key_by_strategy_and_symbol(strategy_id=strategy_id, symbol=symbol)

    @staticmethod
    def run_backtest(st_instance_id):
        result: BacktestResults = backtest_main(st_instance_id)

    @staticmethod
    def list_record_by_key(key: str):
        pass
