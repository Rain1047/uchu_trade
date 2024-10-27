import backtrader as bt
import pandas as pd
import numpy as np


# 自定义数据源类
class SignalData(bt.feeds.PandasData):
    lines = ('buy_sig', 'sell_sig', 'stop_loss',)
    params = (
        ('buy_sig', -1),
        ('sell_sig', -1),
        ('stop_loss', -1),
        ('take_profit', -1),
    )


# 策略类
class EnhancedSignalStrategy(bt.Strategy):
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

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def calculate_position_size(self, price, stop_loss):
        risk_per_trade = self.broker.getvalue() * (self.p.risk_percent / 100)
        price_risk = price - stop_loss
        if price_risk <= 0:
            return 0

        position_size = risk_per_trade / price_risk
        max_size = (self.broker.getvalue() * self.p.max_position_size) / price
        position_size = min(position_size, max_size)

        return position_size

    def update_trailing_stop(self):
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


def generate_sample_data():
    data = {
        'datetime': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'open': np.random.rand(100) * 100,
        'high': np.random.rand(100) * 100,
        'low': np.random.rand(100) * 100,
        'close': np.random.rand(100) * 100,
        'volume': np.random.randint(1, 100, size=100),
        'buy_sig': np.random.randint(0, 2, size=100),
        'sell_sig': np.random.randint(0, 2, size=100),
        'stop_loss': np.random.rand(100) * 100,
    }
    return pd.DataFrame(data)


def run_backtest(df, initial_cash=100000.0, risk_percent=2.0, commission=0.001):
    cerebro = bt.Cerebro()

    # 在设置 datetime 列之前先重置索引
    df.reset_index(drop=False, inplace=True)

    data = SignalData(
        dataname=df,
        datetime='datetime',  # 使用 datetime 列名
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

    cerebro.adddata(data)
    cerebro.addstrategy(EnhancedSignalStrategy, risk_percent=risk_percent)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    print(f'初始投资组合价值: ${initial_cash:.2f}')

    results = cerebro.run()
    strat = results[0]

    portfolio_value = cerebro.broker.getvalue()
    returns = strat.analyzers.returns.get_analysis()
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trades = strat.analyzers.trades.get_analysis()

    print('\n=== 回测结果 ===')
    print(f'最终投资组合价值: ${portfolio_value:.2f}')
    print(f'总收益率: {returns["rtot"]:.2%}')
    print(f'年化收益率: {returns.get("rnorm", 0):.2%}')
    # 添加检查夏普比率
    sharpe_ratio = sharpe.get("sharperatio")
    if sharpe_ratio is None:
        print('夏普比率: 无法计算')
    else:
        print(f'夏普比率: {sharpe_ratio:.3f}')
    print(f'最大回撤: {drawdown["max"]["drawdown"]:.2%}')
    print(f'最大回撤金额: ${drawdown["max"]["moneydown"]:.2f}')

    if trades.get('total'):
        print('\n=== 交易统计 ===')
        print(f'总交易次数: {trades["total"]["total"]}')
        print(f'盈利交易次数: {trades["won"]["total"]}')
        print(f'亏损交易次数: {trades["lost"]["total"]}')
        if trades["won"]["total"]:
            print(f'平均盈利: ${trades["won"]["pnl"]["average"]:.2f}')
        if trades["lost"]["total"]:
            print(f'平均亏损: ${trades["lost"]["pnl"]["average"]:.2f}')

    cerebro.plot(style='candlestick')


if __name__ == '__main__':
    df = generate_sample_data()
    print(df.head(10))
    run_backtest(df, initial_cash=100000.0, risk_percent=2.0)
