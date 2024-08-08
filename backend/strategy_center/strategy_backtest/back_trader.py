import backtrader as bt
import datetime
import strategy_double_bollinger_bands_buy as buy_strategy
import strategy_60_day_breakthrough_sell as sell_strategy


class CombinedStrategy(bt.Strategy):
    params = (
        ('buy_signal', None),
        ('sell_signal', None),
    )

    def __init__(self):
        self.buy_signal = self.params.buy_signal(self.data)
        self.sell_signal = self.params.sell_signal(self.data)

    def next(self):
        if not self.position:
            if self.buy_signal():
                self.buy()
        elif self.sell_signal():
            self.sell()


def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(
        CombinedStrategy,
        buy_signal=buy_strategy.BuyStrategy,
        sell_signal=sell_strategy.SellStrategy
    )

    # 读取本地 CSV 文件
    data = bt.feeds.GenericCSVData(
        dataname='AAPL.csv',
        dtformat=('%Y-%m-%d'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=6,
        reverse=False
    )

    cerebro.adddata(data)
    cerebro.broker.set_cash(10000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()


if __name__ == '__main__':
    run_backtest()
