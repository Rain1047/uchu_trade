import backtrader as bt


class BuyStrategy:
    def __init__(self, data):
        self.data = data
        self.bb = bt.indicators.BollingerBands(self.data, period=20)
        self.lowerband = self.bb.lines.bot

    def __call__(self):
        return self.data.close[0] < self.lowerband[0]
