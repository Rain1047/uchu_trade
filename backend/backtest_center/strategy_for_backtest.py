from typing import Optional, Any

import backtrader as bt

from backend.backtest_center.models.trade_record import TradeRecord


class StrategyForBacktest(bt.Strategy):
    """改进后的DBB策略，使用动态止损单管理"""

    params = (
        ('risk_percent', 2.0),
        ('max_position_size', 0.5),
        ('debug', True),  # 添加调试标志
    )

    def __init__(self):
        super().__init__()
        # 数据线
        self.dataclose = self.datas[0].close
        self.entry_sig = self.datas[0].entry_sig
        self.entry_price = self.datas[0].entry_price
        self.sell_sig = self.datas[0].sell_sig
        self.sell_price = self.datas[0].sell_price

        # 订单管理
        self.entry_order = None  # 入场订单
        self.stop_order = None  # 止损订单
        self.buy_price = None  # 买入价格

        # 交易统计
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.trade_records = []
        self.entry_signal_count = 0

        # 调试信息
        self.missed_signals = []

    def log(self, txt: str, dt: Optional[Any] = None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        """订单状态更新处理"""
        if order.status in [order.Submitted, order.Accepted]:
            return

            # 打印止损单状态
        if order.status == order.Canceled:
            if order.status == order.Canceled:
                # 通过exectype判断订单类型更准确
                order_type = "止损单" if order.exectype == bt.Order.Stop else "入场单"
                # self.log(f"订单取消详情 - 订单类型: {order_type}, 当前价格: {self.dataclose[0]:.2f}, "
                #          f"订单价格: {order.price:.2f}, exectype: {order.exectype}")
        if order.status == order.Completed:
            # 记录交易
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

                # 设置初始止损单
                self.place_stop_order()
            else:
                # 计算收益
                if self.buy_price:
                    profit = (order.executed.price - self.buy_price) * abs(order.executed.size)
                    trade_record.pnl = profit
                    self.log(f'卖出执行 - 卖出价格: {order.executed.price:.2f}, '
                             f'买入价格: {self.buy_price:.2f}, '
                             f'卖出仓位: {abs(order.executed.size):.8f}, '
                             f'收益: {profit:.2f}'
                             f'{"(盈利)" if profit > 0 else "(亏损)"}')

                    # 更新统计
                    if profit > 0:
                        self.winning_trades += 1
                    else:
                        self.losing_trades += 1
                    self.trade_count += 1
                    # 重置状态
                    self.buy_price = None
                    self.stop_order = None

            self.trade_records.append(trade_record)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log(f'订单失败 - 状态: {order.getstatusname()}')
            pass

        # 重置相关订单引用
        if order == self.entry_order:
            self.entry_order = None
        elif order == self.stop_order:
            self.stop_order = None

    def place_stop_order(self):
        """
        改进的止损单管理
        - 处理订单取消的情况
        - 添加更多的状态检查
        - 改进日志记录
        """
        if not self.position:
            return

        # 获取价格
        stop_price = self.sell_price[0]
        current_price = self.dataclose[0]
        entry_price = self.buy_price if self.buy_price else current_price

        # 配置参数
        TRAIL_PERCENT = 0.02  # 2% 追踪止损
        USE_TRAIL_STOP = False  # 是否使用追踪止损
        USE_STOP = True  # 是否使用限价止损

        try:
            # 取消现有止损单
            if self.stop_order:
                self.cancel(self.stop_order)
                self.stop_order = None

            # 1. 追踪止损
            if USE_TRAIL_STOP:
                self.stop_order = self.sell(
                    size=self.position.size,
                    exectype=bt.Order.StopTrail,
                    trailpercent=TRAIL_PERCENT
                )
                self.log(f'设置追踪止损单 - 跟踪比例: {TRAIL_PERCENT * 100}%, '
                         f'当前价格: {current_price:.2f}')

            # 2. 限价止损
            elif USE_STOP:
                self.stop_order = self.sell(
                    size=self.position.size,
                    exectype=bt.Order.Stop,
                    price=stop_price,  # 触发价
                )
                # self.log(f'设置限价止损单 - 触发价: {stop_price:.2f}, '
                #          f'当前价格: {current_price:.2f}')

        except Exception as e:
            self.log(f'设置止损单失败: {str(e)}')
            self.stop_order = None

            # 记录止损设置
        # if self.stop_order:
        #     self.log(f'止损单详情 - 类型: {self.stop_order.exectype}, '
        #              f'价格: {getattr(self.stop_order, "price", "N/A")}')

    def next(self):
        """
        改进的策略执行逻辑
        - 添加更多的状态检查
        - 改进止损单管理
        """
        # 统计信号
        if self.entry_sig[0] == 1:
            self.entry_signal_count += 1

        current_price = self.dataclose[0]

        # 处理入场信号 - 不再检查是否有仓位
        if (self.entry_sig[0] == 1 and  # 有入场信号
                not self.entry_order):  # 没有待执行的入场订单

            # 计算新的仓位大小
            size = self.calculate_position_size(current_price)

            if size > 0:
                self.log(f'创建买入订单 - 价格: {current_price:.2f}, '
                         f'数量: {size:.8f}, '
                         f'当前持仓: {self.position.size if self.position else 0}')
                self.entry_order = self.buy(size=size)

                # if self.p.debug:
                #     self.log(f'买入信号详情 - '
                #              f'可用资金: {self.broker.getcash():.2f}, '
                #              f'总资产: {self.broker.getvalue():.2f}, '
                #              f'现有持仓: {self.position.size if self.position else 0}')

        # 止损单管理 - 只要有仓位就管理止损单
        if self.position:
            # 获取最新止损价
            stop_price = self.sell_price[0]

            # 检查是否需要更新止损单
            if not self.stop_order:
                # 没有止损单，创建新的
                self.place_stop_order()
            elif abs(self.stop_order.price - stop_price) > 0.01:
                # 止损价格有变化，更新止损单
                self.cancel(self.stop_order)
                self.place_stop_order()

            # if self.p.debug:
            #     self.log(f'仓位状态 - '
            #              f'持仓量: {self.position.size:.8f}, '
            #              f'当前价格: {current_price:.2f}, '
            #              f'止损价格: {stop_price:.2f}')

    def calculate_position_size(self, price: float) -> float:
        """
        改进的仓位计算:
        - 考虑现有持仓
        - 基于总资产计算新仓位
        """
        # 计算目标交易价值
        portfolio_value = self.broker.getvalue()
        trade_value = portfolio_value * (self.p.risk_percent / 100)

        # 计算最大允许的总仓位价值
        max_position_value = portfolio_value * self.p.max_position_size

        # 计算现有仓位价值
        current_position_value = self.position.size * price if self.position else 0

        # 计算还可以增加的仓位价值
        available_position_value = max_position_value - current_position_value

        # 确定本次交易的目标价值
        target_trade_value = min(trade_value, available_position_value)

        # 如果可用金额太小，返回0
        if target_trade_value < price * 0.001:  # 最小交易单位
            if self.p.debug:
                self.log(f'仓位太小 - 目标交易价值: {target_trade_value:.2f}, '
                         f'最小要求: {price * 0.001:.2f}')
            return 0

        # 计算实际可以购买的数量
        size = target_trade_value / price

        return size

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
