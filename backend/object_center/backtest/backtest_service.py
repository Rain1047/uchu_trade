from backend.backtest_center.backtest_main import *
from backend.backtest_center.models.backtest_result import BacktestResults
from backend.object_center._object_dao.backtest_record import BacktestRecord
from backend.object_center._object_dao.backtest_result import BacktestResult
from backend.object_center._object_dao.symbol_instance import SymbolInstance


class BacktestService:

    @staticmethod
    def list_symbol() -> list:
        return SymbolInstance.query_all_usdt()
    # {'data': ['BTC-USDT', 'SOL-USDT', 'ETH-USDT', 'DOGE-USDT']}

    @staticmethod
    def list_strategy_by_symbol(symbol: str) -> list:
        return StrategyInstance.list_by_trade_pair(trade_pair=symbol)

    #
    # {'success': True, 'data': [
    #     {'id': 6, 'name': '测试策略', 'trade_pair': 'BTC-USDT', 'side': 'short', 'entry_per_trans': 12.0,
    #      'loss_per_trans': -3.0, 'time_frame': '30m', 'entry_st_code': 'dbb_strategy', 'exit_st_code': 'Exit2',
    #      'filter_st_code': 'Filter3', 'stop_loss_config': '{"stop_limit": "9", "trailing_stop": "89"}',
    #      'schedule_config': '{"date": "3,5,6", "time": "0-10"}', 'switch': 0, 'is_del': 0, 'env': 'dev',
    #      'gmt_create': '2024-11-10 14:36:10', 'gmt_modified': '2024-11-30 10:22:37'},
    #     {'id': 8, 'name': 'BTC双布林带策略', 'trade_pair': 'BTC-USDT', 'side': 'long', 'entry_per_trans': 1000.0,
    #      'loss_per_trans': 200.0, 'time_frame': '4H', 'entry_st_code': 'dbb_entry_long_strategy',
    #      'exit_st_code': 'dbb_exit_long_strategy', 'filter_st_code': 'Filter1,Filter2',
    #      'stop_loss_config': '{"trailing_stop": "12"}', 'schedule_config': '{"date": "1,2", "time": "12-23"}',
    #      'switch': 1, 'is_del': 0, 'env': 'dev', 'gmt_create': '2024-11-12 22:18:05',
    #      'gmt_modified': '2024-11-30 10:22:21'}]}

    @staticmethod
    def list_key(strategy_id: str, symbol: str):
        return BacktestResult.list_key_by_strategy_and_symbol(strategy_id=strategy_id, symbol=symbol)

    # {'success': True, 'data': ['BTC-USDT_ST8_202412022210', 'BTC-USDT_ST8_202412022208', 'BTC-USDT_ST8_202412022205',
    #                            'BTC-USDT_ST8_202412020017', 'BTC-USDT_ST8_202412012312']}

    @staticmethod
    def run_backtest(st_instance_id):
        return backtest_main(st_instance_id)
    # {'success': True,
    #  'data': {'initial_value': 100000.0, 'final_value': 101801.6119191148, 'total_return': 0.017855752178952206,
    #           'annual_return': 0.013361783830799084, 'sharpe_ratio': -0.11011698955825451,
    #           'max_drawdown': 0.43074964153891127, 'max_drawdown_amount': 434.76787154827616, 'total_trades': 85,
    #           'winning_trades': 31, 'losing_trades': 54, 'avg_win': 113.26613022175843, 'avg_loss': -31.6599651437001,
    #           'win_rate': 36.470588235294116, 'total_entry_signals': 113, 'total_sell_signals': 77,
    #           'key': 'BTC双布林带策略_ST8_202412042237'}}

    @staticmethod
    def list_record_by_key(key: str):
        return BacktestRecord.list_by_key(key)
        # {'success': True, 'data': [
        #     {'id': 784, 'back_test_result_key': 'BTC-USDT_ST8_202412022210', 'transaction_time': '2024-01-01',
        #      'transaction_result': 'Price: 42283.58, Size: -0.04692738269092875, PnL: -15.742259797498917',
        #      'transaction_pnl': -15.74},
        #     {'id': 785, 'back_test_result_key': 'BTC-USDT_ST8_202412022210', 'transaction_time': '2024-01-03',
        #      'transaction_result': 'Price: 44882.86162772353, Size: -0.04683991805260332, PnL: 102.70362256047731',
        #      'transaction_pnl': 102.7}
        # )}

    @staticmethod
    def get_backtest_detail(key):
        return BacktestResult.get_by_key(key)

    # {'success': True,
    #  'data': {'id': 7, 'back_test_result_key': 'BTC-USDT_ST8_202412022210', 'symbol': 'BTC-USDT', 'strategy_id': '8',
    #           'strategy_name': 'BTC双布林带策略', 'test_finished_time': '2024-12-02 22:10:34',
    #           'buy_signal_count': b'o\x00\x00\x00\x00\x00\x00\x00',
    #           'sell_signal_count': b'K\x00\x00\x00\x00\x00\x00\x00', 'transaction_count': 84, 'profit_count': 31,
    #           'loss_count': 53, 'profit_total_count': 1802, 'profit_average': 40, 'profit_rate': 36,
    #           'gmt_create': '2024-12-02 22:10:34', 'gmt_modified': '2024-12-02 22:10:34'}}


if __name__ == '__main__':
    result = BacktestService.get_backtest_detail('BTC-USDT_ST8_202412022210')
    print({
        "success": True,
        "data": result
    })
