import backtrader as bt
import pandas as pd

from tvDatafeed import Interval

from backend.backtest_center.strategies.Improved_dbb_strategy import ImprovedDBBStrategy
from backend.backtest_center.data_feeds.signal_data import SignalData
from backend.backtest_center.models.backtest_result import BacktestResults
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import dbb_entry_long_strategy_backtest
from backend.strategy_center.atom_strategy.exit_strategy.dbb_exist_strategy import dbb_exist_strategy_for_backtest


def _print_results(results: BacktestResults) -> None:
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
        self.cerebro.addstrategy(ImprovedDBBStrategy, risk_percent=self.risk_percent)
        self._add_analyzers()

    def _add_analyzers(self) -> None:
        """添加分析器"""
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

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
            entry_sig='entry_sig',
            entry_price='entry_price',
            sell_sig='sell_sig',
            sell_price='sell_price'
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

    def _export_trade_records(self, results) -> None:
        """导出交易记录到Excel"""
        strategy = results[0]
        if not strategy.trade_records:
            return

        records_df = pd.DataFrame([vars(record) for record in strategy.trade_records])

        # 添加累计收益列
        records_df['cumulative_pnl'] = records_df['pnl'].cumsum()

        # 添加其他统计信息
        stats_df = pd.DataFrame([{
            'Initial Value': self.initial_cash,
            'Final Value': self.cerebro.broker.getvalue(),
            'Total Return': f"{(self.cerebro.broker.getvalue() / self.initial_cash - 1) * 100:.2f}%",
            'Win Rate': f"{(len(records_df[records_df['pnl'] > 0]) / len(records_df) * 100):.2f}%" if len(
                records_df) > 0 else "0%",
            'Total Trades': len(records_df)
        }])

        # 导出到Excel，创建多个sheet
        with pd.ExcelWriter('backtest_results.xlsx') as writer:
            records_df.to_excel(writer, sheet_name='Trade Records', index=False)
            stats_df.to_excel(writer, sheet_name='Summary', index=False)

    def run(self, df: pd.DataFrame, plot: bool = True) -> BacktestResults:
        """运行回测"""
        self.prepare_data(df)
        results = self.cerebro.run()
        backtest_results = self._process_results(results)
        # 导出交易记录
        self._export_trade_records(results)

        _print_results(backtest_results)

        if plot:
            self.cerebro.plot(style='candlestick')

        return backtest_results


def main():
    """主函数"""
    # 创建回测系统实例
    backtest = BacktestSystem(initial_cash=100000.0, risk_percent=2.0, commission=0.001)

    # 准备数据
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_4_hour)
    df = pd.read_csv(f"{file_abspath}")

    # 执行策略生成信号
    df = dbb_entry_long_strategy_backtest(df)
    df = dbb_exist_strategy_for_backtest(df)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[df['datetime'] > "2023-12-31 08:00:00"]

    # 打印生成的信号统计
    total_entry_signals = df['entry_sig'].sum()
    total_sell_signals = df['sell_sig'].sum()
    print(f"\n信号统计:")
    print(f"总买入信号数: {total_entry_signals}")
    print(f"总卖出信号数: {total_sell_signals}")

    # 运行回测
    results = backtest.run(df, plot=True)


if __name__ == '__main__':
    main()
