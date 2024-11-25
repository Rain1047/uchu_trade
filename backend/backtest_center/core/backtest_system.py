import backtrader as bt
import pandas as pd
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from backend.backtest_center.data_feeds.signal_data import SignalData
from backend.backtest_center.models.backtest_result import BacktestResults
from backend.backtest_center.strategies.common_strategy import CommonStrategy
from backend.backtest_center.utils.results_printer import ResultsPrinter

logger = logging.getLogger(__name__)


class BacktestSystem:
    """
    回测系统主类

    负责:
    - 初始化和配置回测环境
    - 加载和预处理数据
    - 运行回测
    - 处理和导出结果
    """

    def __init__(
            self,
            initial_cash: float = 100000.0,
            risk_percent: float = 2.0,
            commission: float = 0.001,
            config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化回测系统

        Args:
            initial_cash: 初始资金
            risk_percent: 风险百分比
            commission: 手续费率
            config: 其他配置参数
        """
        self.initial_cash = initial_cash
        self.risk_percent = risk_percent
        self.commission = commission
        self.config = config or {}

        self.cerebro = bt.Cerebro()
        self._setup_cerebro()

    def _setup_cerebro(self) -> None:
        """配置cerebro实例"""
        # 设置基本参数
        self.cerebro.broker.setcash(self.initial_cash)
        self.cerebro.broker.setcommission(commission=self.commission)

        # 添加策略
        self.cerebro.addstrategy(
            CommonStrategy,
            risk_percent=self.risk_percent
        )

        # 添加分析器
        self._add_analyzers()

    def _add_analyzers(self) -> None:
        """添加分析器"""
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    def prepare_data(self, df: pd.DataFrame) -> None:
        """
        准备数据

        Args:
            df: 包含交易数据的DataFrame
        """
        try:
            # 数据预处理
            df = self._preprocess_data(df)

            # 创建数据源
            data = SignalData.from_dataframe(df)

            # 添加数据
            self.cerebro.adddata(data)

        except Exception as e:
            logger.error(f"数据准备失败: {str(e)}")
            raise

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理

        Args:
            df: 原始DataFrame

        Returns:
            pd.DataFrame: 处理后的DataFrame
        """
        df = df.copy()

        # 确保日期时间格式正确
        df['datetime'] = pd.to_datetime(df['datetime'])

        # 确保数值列为浮点型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume',
                           'entry_sig', 'entry_price', 'sell_sig', 'sell_price']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 处理缺失值
        df = df.dropna()

        return df

    def _process_results(self, results) -> BacktestResults:
        """
        处理回测结果

        Args:
            results: backtrader的回测结果

        Returns:
            BacktestResults: 处理后的回测结果对象
        """
        strat = results[0]

        # 获取各种分析结果
        portfolio_value = self.cerebro.broker.getvalue()
        returns = strat.analyzers.returns.get_analysis()
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        # 提取交易统计
        total_trades = trades.get('total', {}).get('total', 0)
        winning_trades = trades.get('won', {}).get('total', 0)
        losing_trades = trades.get('lost', {}).get('total', 0)
        avg_win = trades.get('won', {}).get('pnl', {}).get('average', 0)
        avg_loss = trades.get('lost', {}).get('pnl', {}).get('average', 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        return BacktestResults(
            initial_value=self.initial_cash,
            final_value=portfolio_value,
            total_return=returns.get('rtot', 0),
            annual_return=returns.get('rnorm', 0),
            sharpe_ratio=sharpe.get('sharperatio', 0),
            max_drawdown=drawdown.get('max', {}).get('drawdown', 0),
            max_drawdown_amount=drawdown.get('max', {}).get('moneydown', 0),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            win_rate=win_rate
        )

    def run(self, df: pd.DataFrame, plot: bool = True) -> BacktestResults:
        """
        运行回测

        Args:
            df: 输入数据
            plot: 是否绘制图表

        Returns:
            BacktestResults: 回测结果
        """
        try:
            # 准备数据
            self.prepare_data(df)

            # 运行回测
            results = self.cerebro.run()

            # 处理结果
            backtest_results = self._process_results(results)

            # 打印结果
            ResultsPrinter.print_results(backtest_results)

            # 导出交易记录
            if results[0].trade_records:
                ResultsPrinter.export_trade_records(
                    records=results[0].trade_records,
                    stats={
                        'Initial Value': self.initial_cash,
                        'Final Value': self.cerebro.broker.getvalue(),
                        'Total Return': f"{(self.cerebro.broker.getvalue() / self.initial_cash - 1) * 100:.2f}%",
                        'Win Rate': f"{backtest_results.win_rate:.2f}%",
                        'Total Trades': backtest_results.total_trades
                    }
                )

            # 绘制图表
            if plot:
                self.cerebro.plot(style='candlestick')

            return backtest_results

        except Exception as e:
            logger.error(f"回测执行失败: {str(e)}")
            raise
