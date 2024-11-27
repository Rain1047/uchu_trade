from typing import Optional, Any

import backtrader as bt

from backend.backtest_center.models.trade_record import TradeRecord


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

    def place_stop_order(self):
        """
        改进的止损单管理
        - 处理订单取消的情况
        - 添加更多的状态检查
        - 改进日志记录
        """
        if not self.position:
            return

        # 获取最新的止损价格
        stop_price = self.sell_price[0]
        current_price = self.dataclose[0]

        # 检查止损价格是否有效
        if stop_price <= 0:
            self.log(f'无效的止损价格: {stop_price}，跳过止损单设置', level='WARNING')
            return

        # 如果止损价格高于当前价格，使用市价单
        if stop_price <= current_price:
            self.log(f'止损价格 ({stop_price:.2f}) 低于当前价格 ({current_price:.2f})，执行市价卖出')
            if self.stop_order:
                self.cancel(self.stop_order)
            self.stop_order = self.sell(
                size=self.position.size,
                exectype=bt.Order.Market
            )
            return

        # 检查是否需要更新止损单
        if self.stop_order:
            # 如果价格相同，无需更新
            if abs(self.stop_order.price - stop_price) < 0.01:  # 添加一个小的容差
                return
            # 取消旧的止损单
            self.cancel(self.stop_order)

        try:
            # 创建新的止损单
            self.stop_order = self.sell(
                size=self.position.size,
                exectype=bt.Order.Stop,
                price=stop_price
            )

            self.log(f'设置新止损单 - 价格: {stop_price:.2f}, '
                     f'持仓: {self.position.size:.8f}, '
                     f'当前价格: {current_price:.2f}')

        except Exception as e:
            self.log(f'设置止损单失败: {str(e)}', level='ERROR')

    def next(self):
        """
        改进的策略执行逻辑
        - 添加更多的状态检查
        - 改进止损单管理
        """
        # 检查是否需要更新止损单
        if self.position and not self.entry_order:
            # 确保当前没有待处理的订单再更新止损单
            if not self.stop_order or not self.stop_order.alive():
                self.place_stop_order()

        # 检查入场信号
        if (not self.position and  # 没有持仓
                not self.entry_order and  # 没有待执行的入场订单
                not self.stop_order and  # 没有待执行的止损单
                self.entry_sig[0] == 1):  # 有入场信号

            # 计算仓位大小
            size = self.calculate_position_size(self.dataclose[0])

            if size > 0:
                self.log(f'创建买入订单 - 价格: {self.dataclose[0]:.2f}, '
                         f'数量: {size:.8f}')
                self.entry_order = self.buy(size=size)

    def stop(self):
        """
        策略结束时的统计
        修复了信号统计的问题
        """
        # 计算胜率
        win_rate = (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0

        # 统计信号 - 使用lines的队列方式而不是直接访问数组
        entry_signals = 0
        for i in range(0, len(self.data0)):
            if self.entry_sig[0 - i] == 1:  # 使用相对索引
                entry_signals += 1

        # 输出最终统计
        self.log(f'策略结束统计:')
        self.log(f'总交易次数: {self.trade_count}')
        self.log(f'盈利交易: {self.winning_trades}')
        self.log(f'亏损交易: {self.losing_trades}')
        self.log(f'胜率: {win_rate:.2f}%')
        self.log(f'入场信号总数: {entry_signals}')

        # 如果需要检查止损单状态
        if self.stop_order:
            self.log('策略结束时有未完成的止损单')
            if self.position:
                self.log(f'最后持仓: {self.position.size:.8f}')
