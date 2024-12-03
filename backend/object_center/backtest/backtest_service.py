from backend.backtest_center.backtest_main import *
from backend.backtest_center.models.backtest_result import BacktestResults
from backend.object_center.object_dao.backtest_record import BacktestRecord
from backend.object_center.object_dao.backtest_result import BacktestResult
from backend.object_center.object_dao.symbol_instance import SymbolInstance


class BacktestService:

    @staticmethod
    def list_symbol() -> dict:
        return SymbolInstance.query_all_usdt()
    # {'symbol_list': ['BTC-USDT', 'SOL-USDT', 'ETH-USDT', 'DOGE-USDT']}

    @staticmethod
    def list_strategy_by_symbol() -> dict:
        pass

    @staticmethod
    def list_key(strategy_id: str, symbol: str):
        return BacktestResult.list_key_by_strategy_and_symbol(strategy_id=strategy_id, symbol=symbol)

    @staticmethod
    def run_backtest(st_instance_id):
        result: BacktestResults = backtest_main(st_instance_id)
        return result

    @staticmethod
    def list_record_by_key(key: str):
        return BacktestRecord.list_by_key(key)

    @staticmethod
    def get_backtest_detail(key):
        return BacktestResult.get_by_key(key)


if __name__ == '__main__':
    result = BacktestService.list_symbol()
    print(result)
