import backtrader as bt
import pandas as pd
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from tvDatafeed import Interval

from backend.backtest_center.models.trade_record import TradeRecord


class FixedInvestmentStrategy(bt.Strategy):
    """固定投资金额的交易策略"""

    params = (
        ('risk_percent', 2.0),
        ('fixed_value', 100000.0),  # 每次固定投入1000美元
        ('debug', True),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.entry_sig = self.datas[0].entry_sig
        self.entry_price = self.datas[0].entry_price
        self.sell_sig = self.datas[0].sell_sig
        self.sell_price = self.datas[0].sell_price

        # 订单管理
        self.entry_order = None
        self.stop_order = None
        self.buy_price = None

        # 交易统计
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.trade_records = []
        self.entry_signal_count = 0

        # 投资统计
        self.total_invested = 0
        self.active_positions = []

        # 日志设置
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, txt: str, dt: Optional[datetime] = None):
        """日志记录"""
        dt = dt or self.datas[0].datetime.date(0)
        self.logger.info(f'{dt.isoformat()} {txt}')

    def calculate_position_size(self, price: float) -> float:
        """计算购买数量"""
        return self.p.fixed_value / price

    def next(self):
        """策略主逻辑"""
        if self.entry_sig[0] == 1:
            self.entry_signal_count += 1
            current_price = self.dataclose[0]

            # 检查是否可以创建新的买入订单
            if not self.entry_order:
                size = self.calculate_position_size(current_price)
                self.log(f'创建买入订单 - 价格: {current_price:.2f}, '
                         f'数量: {size:.8f}, '
                         f'金额: {self.p.fixed_value:.2f}')
                self.entry_order = self.buy(size=size)
                self.total_invested += self.p.fixed_value

        # 止损单管理
        if self.position:
            stop_price = self.sell_price[0]
            # 检查是否需要更新止损单
            if not self.stop_order:
                self.place_stop_order()
            elif abs(self.stop_order.price - stop_price) > 0.01:
                self.cancel(self.stop_order)
                self.place_stop_order()

    def place_stop_order(self):
        """设置止损单"""
        if not self.position:
            return

        stop_price = self.sell_price[0]
        current_price = self.dataclose[0]

        try:
            self.stop_order = self.sell(
                size=self.position.size,
                exectype=bt.Order.Stop,
                price=stop_price
            )

            self.log(f'设置止损单 - 价格: {stop_price:.2f}, '
                     f'持仓: {self.position.size:.8f}, '
                     f'当前价格: {current_price:.2f}')

        except Exception as e:
            self.log(f'设置止损单失败: {str(e)}')

    def notify_order(self, order):
        """订单状态更新处理"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            # 创建交易记录
            trade_record = TradeRecord(
                datetime=self.data.datetime.date(0).isoformat(),
                action='BUY' if order.isbuy() else 'SELL',
                price=order.executed.price,
                size=order.executed.size,
                value=order.executed.value,
                commission=order.executed.comm
            )

            if order.isbuy():
                self.buy_price = order.executed.price
                self.log(f'买入执行 - 价格: {order.executed.price:.2f}, '
                         f'数量: {order.executed.size:.8f}, '
                         f'金额: {order.executed.value:.2f}')

                position = {
                    'size': order.executed.size,
                    'price': order.executed.price,
                    'value': order.executed.value,
                    'date': self.data.datetime.date(0)
                }
                self.active_positions.append(position)
                self.place_stop_order()
            else:
                if self.buy_price:
                    profit = (order.executed.price - self.buy_price) * order.executed.size
                    trade_record.pnl = profit
                    self.log(f'卖出执行 - 价格: {order.executed.price:.2f}, '
                             f'收益: {profit:.2f}')
                    if profit > 0:
                        self.winning_trades += 1
                    else:
                        self.losing_trades += 1
                    self.trade_count += 1
                self.buy_price = None
                self.stop_order = None

            self.trade_records.append(trade_record)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            order_type = "入场" if order == self.entry_order else "止损"
            self.log(f'{order_type}订单失败 - 状态: {order.getstatusname()}')

        if order == self.entry_order:
            self.entry_order = None
        elif order == self.stop_order:
            self.stop_order = None

    def stop(self):
        """策略结束时的统计"""
        final_value = self.broker.getvalue()
        total_return = (final_value / self.total_invested - 1) * 100 if self.total_invested > 0 else 0
        win_rate = (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0

        self.log('\n=== 策略执行统计 ===')
        self.log(f'总投入金额: ${self.total_invested:.2f}')
        self.log(f'最终价值: ${final_value:.2f}')
        self.log(f'总收益率: {total_return:.2f}%')
        self.log(f'总信号数: {self.entry_signal_count}')
        self.log(f'实际交易数: {self.trade_count}')
        self.log(f'胜率: {win_rate:.2f}%')
        self.log(f'盈利交易: {self.winning_trades}')
        self.log(f'亏损交易: {self.losing_trades}')

        if self.position:
            current_value = self.position.size * self.dataclose[0]
            self.log('\n=== 最终持仓 ===')
            self.log(f'持仓数量: {self.position.size:.8f}')
            self.log(f'持仓价值: ${current_value:.2f}')
            if self.stop_order:
                self.log(f'止损单价格: ${self.stop_order.price:.2f}')