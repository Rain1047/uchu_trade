import backtrader as bt

class SellStrategy:
    def __init__(self, data):
        self.data = data
        self.highest = bt.indicators.Highest(self.data.close, period=60)

    def __call__(self):
        return self.data.close[0] > self.highest[0]
