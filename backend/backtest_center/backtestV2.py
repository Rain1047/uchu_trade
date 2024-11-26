import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass

from tvDatafeed import Interval

from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import dbb_entry_long_strategy_backtest
from backend.strategy_center.atom_strategy.exit_strategy.dbb_exist_strategy import dbb_exist_strategy_for_backtest


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


# 首先添加Trade记录类
@dataclass
class TradeRecord:
    """交易记录数据类"""
    datetime: str
    action: str  # 'BUY' or 'SELL'
    price: float
    size: float
    value: float
    commission: float
    pnl: float = 0.0  # 仅在卖出时有效


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


class SignalData(bt.feeds.PandasData):
    """自定义数据源类"""
    lines = ('entry_sig', 'entry_price', 'sell_sig', 'sell_price',)
    params = (
        ('entry_sig', -1),
        ('entry_price', -1),
        ('sell_sig', -1),
        ('sell_price', -1),
    )


class DBBStrategy(bt.Strategy):
    """交易策略类"""
    params = (
        ('risk_percent', 2.0),
        ('max_position_size', 0.5),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.entry_sig = self.datas[0].entry_sig
        self.entry_price = self.datas[0].entry_price
        self.sell_sig = self.datas[0].sell_sig
        self.sell_price = self.datas[0].sell_price

        self.order = None
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.buy_price = None
        self.trade_records = []  # 添加交易记录列表

    def log(self, txt: str, dt: Optional[Any] = None) -> None:
        """日志函数"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            try:
                trade_record = TradeRecord(
                    datetime=self.data.datetime.date(0).isoformat(),
                    action='BUY' if order.isbuy() else 'SELL',
                    price=order.executed.price,
                    size=order.executed.size,
                    value=order.executed.value,
                    commission=order.executed.comm
                )

                if order.isbuy():
                    self.log(f'买入执行: 价格: {order.executed.price:.2f}, '
                             f'成本: {order.executed.value:.2f}, '
                             f'手续费: {order.executed.comm:.2f}, '
                             f'当前总持仓: {self.position.size:.8f}')
                    self.buy_price = order.executed.price
                else:
                    self.log(f'卖出执行: 价格: {order.executed.price:.2f}, '
                             f'成本: {order.executed.value:.2f}, '
                             f'手续费: {order.executed.comm:.2f}')

                    if self.buy_price:
                        profit = (order.executed.price - self.buy_price) * order.executed.size
                        trade_record.pnl = profit
                        self.log(f'交易收益: {profit:.2f}')
                        if profit > 0:
                            self.winning_trades += 1
                        else:
                            self.losing_trades += 1
                        self.trade_count += 1
                        self.buy_price = None

                self.trade_records.append(trade_record)
            except Exception as e:
                self.log(f'处理订单时出现错误: {str(e)}')

        elif order.status in [order.Canceled]:
            self.log(f'订单已取消')
        elif order.status in [order.Margin]:
            self.log(f'保证金不足')
        elif order.status in [order.Rejected]:
            self.log(f'订单被拒绝')
        elif order.status in [order.Expired]:
            self.log(f'订单过期')
        else:
            self.log(f'订单状态: {order.status}')

        if order.status != order.Completed:
            order_info = {
                'status': order.status,
                'size': getattr(order, 'size', 'N/A'),
                'price': getattr(order, 'price', 'N/A'),
                'exectype': getattr(order, 'exectype', 'N/A'),
                'info': getattr(order, 'info', 'N/A')
            }
            self.log(f'订单详情: {order_info}')

        self.order = None

    def notify_trade(self, trade):
        """交易状态通知"""
        if trade.isclosed:
            self.log(f'交易利润: 毛利润 {trade.pnl:.2f}, 净利润 {trade.pnlcomm:.2f}')

    def calculate_position_size(self, price: float) -> float:
        # 计算每笔交易的资金量
        cash = self.broker.getcash()
        trade_value = cash * (self.p.risk_percent / 100)

        # 计算可以购买的数量
        size = trade_value / price

        # 考虑当前总仓位
        current_value = self.broker.getvalue()
        max_total_position = current_value * self.p.max_position_size
        current_position_value = self.position.size * price if self.position else 0
        remaining_position_value = max_total_position - current_position_value

        # 确保不超过最大总仓位
        max_additional_size = remaining_position_value / price if remaining_position_value > 0 else 0
        position_size = min(size, max_additional_size)

        # 如果计算出的仓位太小，就不开仓
        min_size = 0.001
        if position_size < min_size:
            return 0

        return max(position_size, min_size)

    def next(self):
        """策略逻辑"""
        if self.order:
            return

        # 处理买入信号
        if self.entry_sig[0] == 1:
            current_price = self.dataclose[0]
            size = self.calculate_position_size(current_price)

            if size > 0:
                self.log(f'买入信号触发，当前持仓: {self.position.size if self.position else 0}, '
                         f'价格: {current_price:.2f}, 买入数量: {size:.8f}, '
                         f'可用资金: {self.broker.getcash():.2f}')
                try:
                    self.order = self.buy(size=size)
                except Exception as e:
                    self.log(f'创建买入订单失败: {str(e)}')
            else:
                self.log(f'买入信号触发但仓位计算为0，跳过交易')

        # 处理卖出信号
        if self.position and self.sell_sig[0] == 1:
            try:
                current_price = self.dataclose[0]
                sell_price = self.sell_price[0]

                self.log(f'卖出信号触发, 当前持仓: {self.position.size}, '
                         f'当前价格: {current_price:.2f}, 止损价格: {sell_price:.2f}')

                if current_price < sell_price:
                    self.log(f'价格低于止损价，市价卖出')
                    self.order = self.sell(size=self.position.size,
                                           exectype=bt.Order.Market)
                else:
                    self.log(f'设置止损限价单')
                    self.order = self.sell(size=self.position.size,
                                           exectype=bt.Order.Stop,
                                           price=sell_price)
            except Exception as e:
                self.log(f'创建卖出订单失败: {str(e)}')

    def stop(self):
        """策略结束时的统计"""
        win_rate = (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0
        self.log(f'策略统计: 总交易次数: {self.trade_count}, '
                 f'盈利交易: {self.winning_trades}, '
                 f'亏损交易: {self.losing_trades}, '
                 f'胜率: {win_rate:.2f}%')

        # 修改信号统计方式
        entry_signals = 0
        exit_signals = 0

        # 使用 lines 接口获取信号数据
        for i in range(len(self.data)):
            if self.entry_sig.array[i] == 1:
                entry_signals += 1
            if self.sell_sig.array[i] == 1:
                exit_signals += 1

        self.log(f'信号统计: 总买入信号: {entry_signals}, '
                 f'总卖出信号: {exit_signals}, '
                 f'实际交易次数: {self.trade_count}')


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
        self.cerebro.addstrategy(DBBStrategy, risk_percent=self.risk_percent)
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
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_daily)
    df = pd.read_csv(f"{file_abspath}")

    # 执行策略生成信号
    df = dbb_entry_long_strategy_backtest(df)
    df = dbb_exist_strategy_for_backtest(df)
    df['datetime'] = pd.to_datetime(df['datetime'])

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
