import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass
import unittest
import pandas as pd
from tvDatafeed import Interval

from backend.data_center.data_object.dto.strategy_instance import StrategyInstance
from backend.data_center.data_object.enum_obj import EnumTimeFrame
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import dbb_entry_long_strategy_backtest, \
    dbb_entry_strategy


@dataclass
class BacktestResults:
    """回测结果数据类"""
    initial_value: float
    final_value: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_amount: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    win_rate: float


class SignalData(bt.feeds.PandasData):
    """自定义数据源类"""
    lines = ('buy_sig', 'sell_sig', 'stop_loss',)
    params = (
        ('buy_sig', -1),
        ('sell_sig', -1),
        ('stop_loss', -1),
        ('take_profit', -1),
    )


class EnhancedSignalStrategy(bt.Strategy):
    """交易策略类"""
    params = (
        ('risk_percent', 2.0),
        ('trailing_stop', False),
        ('trailing_percent', 1.0),
        ('max_position_size', 0.5),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.buy_sig = self.datas[0].buy_sig
        self.sell_sig = self.datas[0].sell_sig
        self.stop_loss = self.datas[0].stop_loss

        self.order = None
        self.buy_price = None
        self.stop_loss_price = None
        self.trailing_stop_price = None
        self.highest_price = 0
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0

    def log(self, txt: str, dt: Optional[Any] = None) -> None:
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def calculate_position_size(self, price: float, stop_loss: float) -> float:
        risk_per_trade = self.broker.getvalue() * (self.p.risk_percent / 100)
        price_risk = price - stop_loss
        if price_risk <= 0:
            return 0

        position_size = risk_per_trade / price_risk
        max_size = (self.broker.getvalue() * self.p.max_position_size) / price
        return min(position_size, max_size)

    def update_trailing_stop(self) -> None:
        if not self.position or not self.p.trailing_stop:
            return

        current_price = self.dataclose[0]
        if current_price > self.highest_price:
            self.highest_price = current_price
            self.trailing_stop_price = self.highest_price * (1 - self.p.trailing_percent / 100)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行: 价格: {order.executed.price:.2f}, '
                         f'成本: {order.executed.value:.2f}, '
                         f'手续费: {order.executed.comm:.2f}')
                self.buy_price = order.executed.price
                self.highest_price = order.executed.price
            else:
                self.log(f'卖出执行: 价格: {order.executed.price:.2f}, '
                         f'成本: {order.executed.value:.2f}, '
                         f'手续费: {order.executed.comm:.2f}')
                if self.buy_price:
                    profit = (order.executed.price - self.buy_price) * order.executed.size
                    self.log(f'交易收益: {profit:.2f}')
                    if profit > 0:
                        self.winning_trades += 1
                    else:
                        self.losing_trades += 1
                    self.trade_count += 1
                self.buy_price = None
                self.stop_loss_price = None
                self.trailing_stop_price = None
                self.highest_price = 0

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'交易利润: 毛利润 {trade.pnl:.2f}, 净利润 {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        self.update_trailing_stop()

        if self.position:
            effective_stop = max(self.stop_loss[0], self.trailing_stop_price or -float('inf'))
            if self.data.low[0] <= effective_stop:
                self.log(f'触发止损, 止损价格: {effective_stop:.2f}')
                self.order = self.sell(size=self.position.size)
                return

        if not self.position:
            if self.buy_sig[0]:
                size = self.calculate_position_size(self.dataclose[0], self.stop_loss[0])
                if size > 0:
                    self.log(f'买入信号触发, 价格: {self.dataclose[0]:.2f}, '
                             f'数量: {size:.8f}')
                    self.order = self.buy(size=size)
                    self.stop_loss_price = self.stop_loss[0]

        else:
            if self.sell_sig[0]:
                self.log(f'卖出信号触发, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell(size=self.position.size)

    def stop(self):
        winning_rate = (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0
        self.log(f'策略统计: 总交易次数: {self.trade_count}, '
                 f'盈利交易: {self.winning_trades}, '
                 f'亏损交易: {self.losing_trades}, '
                 f'胜率: {winning_rate:.2f}%')


def _print_results(results: BacktestResults) -> None:
    """打印回测结果"""
    print('\n=== 回测结果 ===')
    print(f'初始投资组合价值: ${results.initial_value:.2f}')
    print(f'最终投资组合价值: ${results.final_value:.2f}')
    print(f'总收益率: {results.total_return:.2%}')
    print(f'年化收益率: {results.annual_return:.2%}')
    if results.sharpe_ratio is None:
        print('夏普比率: 无法计算')
    else:
        print(f'夏普比率: {results.sharpe_ratio:.3f}')
    print(f'最大回撤: {results.max_drawdown:.2%}')
    print(f'最大回撤金额: ${results.max_drawdown_amount:.2f}')

    print('\n=== 交易统计 ===')
    print(f'总交易次数: {results.total_trades}')
    print(f'盈利交易次数: {results.winning_trades}')
    print(f'亏损交易次数: {results.losing_trades}')
    print(f'胜率: {results.win_rate:.2f}%')
    if results.winning_trades:
        print(f'平均盈利: ${results.avg_win:.2f}')
    if results.losing_trades:
        print(f'平均亏损: ${results.avg_loss:.2f}')


class BacktestSystem:
    """回测系统主类"""

    def __init__(self, initial_cash: float = 100000.0, risk_percent: float = 2.0,
                 commission: float = 0.001):
        self.initial_cash = initial_cash
        self.risk_percent = risk_percent
        self.commission = commission
        self.cerebro = bt.Cerebro()
        self._setup_cerebro()

    def _setup_cerebro(self) -> None:
        """设置cerebro基本参数"""
        self.cerebro.broker.setcash(self.initial_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        self.cerebro.addstrategy(EnhancedSignalStrategy, risk_percent=self.risk_percent)
        self._add_analyzers()

    def _add_analyzers(self) -> None:
        """添加分析器"""
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    @staticmethod
    def generate_sample_data(periods: int = 100) -> pd.DataFrame:
        """生成样本数据"""
        data = {
            'datetime': pd.date_range(start='2023-01-01', periods=periods, freq='D'),
            'open': np.random.rand(periods) * 100,
            'high': np.random.rand(periods) * 100,
            'low': np.random.rand(periods) * 100,
            'close': np.random.rand(periods) * 100,
            'volume': np.random.randint(1, 100, size=periods),
            'buy_sig': np.random.randint(0, 2, size=periods),
            'sell_sig': np.random.randint(0, 2, size=periods),
            'stop_loss': np.random.rand(periods) * 100,
        }
        return pd.DataFrame(data)

    def prepare_data(self, df: pd.DataFrame) -> None:
        """准备数据"""
        df.reset_index(drop=False, inplace=True)
        data = SignalData(
            dataname=df,
            datetime='datetime',
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            buy_sig='buy_sig',
            sell_sig='sell_sig',
            stop_loss='stop_loss',
            take_profit='take_profit'
        )
        self.cerebro.adddata(data)

    def _process_results(self, results) -> BacktestResults:
        """处理回测结果"""
        strat = results[0]
        portfolio_value = self.cerebro.broker.getvalue()
        returns = strat.analyzers.returns.get_analysis()
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        # 计算交易统计
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
        """运行回测"""
        self.prepare_data(df)
        results = self.cerebro.run()
        backtest_results = self._process_results(results)

        _print_results(backtest_results)

        if plot:
            self.cerebro.plot(style='candlestick')

        return backtest_results


def main():
    """主函数示例"""
    # 创建回测系统实例
    backtest = BacktestSystem(initial_cash=100000.0, risk_percent=2.0, commission=0.001)

    # 生成样本数据
    df = backtest.generate_sample_data()

    # 运行回测
    results = backtest.run(df, plot=True)

    return results


def real_test():
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_daily)
    df = pd.read_csv(f"{file_abspath}")
    df = dbb_entry_strategy(df, None)


if __name__ == '__main__':
    main()
