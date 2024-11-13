import unittest
import pandas as pd
import numpy as np

from backend.service.backtest.backtest import BacktestSystem, BacktestResults


class TestBacktestSystem(unittest.TestCase):
    def setUp(self):
        self.backtest = BacktestSystem(
            initial_cash=100000.0,
            risk_percent=2.0,
            commission=0.001
        )

    def test_generate_sample_data(self):
        sample_data = self.backtest.generate_sample_data()
        self.assertIsInstance(sample_data, pd.DataFrame)
        self.assertEqual(len(sample_data), 100)
        self.assertIn('datetime', sample_data.columns)
        self.assertIn('open', sample_data.columns)
        self.assertIn('high', sample_data.columns)
        self.assertIn('low', sample_data.columns)
        self.assertIn('close', sample_data.columns)
        self.assertIn('volume', sample_data.columns)
        self.assertIn('buy_sig', sample_data.columns)
        self.assertIn('sell_sig', sample_data.columns)
        self.assertIn('stop_loss', sample_data.columns)

    def test_run_backtest(self):
        sample_data = self.backtest.generate_sample_data()
        results = self.backtest.run(sample_data, plot=False)
        self.assertIsInstance(results, BacktestResults)
        self.assertGreater(results.final_value, self.backtest.initial_cash)
        self.assertGreater(results.total_return, 0)
        self.assertGreater(results.annual_return, 0)
        self.assertGreater(results.sharpe_ratio, 0)
        self.assertLess(results.max_drawdown, 0.5)
        self.assertGreater(results.total_trades, 0)
        self.assertGreater(results.winning_trades, 0)
        self.assertLess(results.losing_trades, results.total_trades)
        self.assertGreater(results.win_rate, 50)