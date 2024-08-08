import backtrader as bt
import yfinance as yf

class MyStrategy(bt.Strategy):
    def __init__(self):
        # 初始化布林带指标
        self.upper_band1, self.middle_band, self.lower_band1 = bt.indicators.BBands(self.data.close, period=20, devfactor=1)

    def next(self):
        # 添加买入信号条件
        if self.data.close[0] > self.upper_band1[-1] and self.data.close[-1] < self.upper_band1[-2] and self.data.close[-2] < self.upper_band1[-3]:
            self.buy()

        # 添加退出信号条件
        if len(self) % 4 == 0:
            if self.data.close[0] > self.upper_band1[-1]:
                # 清仓百分之10
                self.sell(size=self.position.size * 0.1)
            elif self.data.close[0] <= self.middle_band[-1]:
                # 全部退出
                self.close()


if __name__ == '__main__':
    # 加载数据
    eth_data = yf.download("ETH-USD", interval="1d", start="2023-01-01", end="2024-01-01")

    eth_data.columns = [col.lower() for col in eth_data.columns]

    eth_data['datetime'] = eth_data.index

    data = bt.feeds.PandasData(dataname=eth_data)

    # 初始化回测引擎
    cerebro = bt.Cerebro()

    # 添加策略
    cerebro.addstrategy(MyStrategy)

    # 添加数据
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.set_cash(10000)

    # 运行回测
    cerebro.run()

    # 输出回测结果
    cerebro.plot()
