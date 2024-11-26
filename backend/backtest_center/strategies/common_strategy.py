from typing import Optional, Dict
import backtrader as bt

from backend.backtest_center.strategies.base_strategy import BaseStrategy


class CommonStrategy(BaseStrategy):
    """
    双布林带策略实现

    参数:
        risk_percent (float): 每次交易的风险百分比
        max_position_size (float): 最大仓位比例
    """

    params = (
        ('risk_percent', 2.0),
        ('max_position_size', 0.5),
    )

    def __init__(self):
        """初始化策略"""
        super().__init__()
        # 数据线
        self.dataclose = self.datas[0].close
        self.entry_sig = self.datas[0].entry_sig
        self.entry_price = self.datas[0].entry_price
        self.sell_sig = self.datas[0].sell_sig
        self.sell_price = self.datas[0].sell_price

        # 交易记录
        self.buy_price = None
        self.trade_records = []

    def calculate_position_size(self, price: float) -> float:
        """
        计算交易规模

        Args:
            price: 当前价格

        Returns:
            float: 计算出的交易规模
        """
        # 计算每笔交易的资金量
        cash = self.broker.getcash()
        trade_value = cash * (self.p.risk_percent / 100)

        # 计算基础持仓规模
        size = trade_value / price

        # 考虑最大仓位限制
        current_value = self.broker.getvalue()
        max_total_position = current_value * self.p.max_position_size
        current_position_value = self.position.size * price if self.position else 0
        remaining_position_value = max_total_position - current_position_value

        # 确保不超过最大仓位
        max_additional_size = remaining_position_value / price if remaining_position_value > 0 else 0
        position_size = min(size, max_additional_size)

        # 确保至少达到最小交易单位
        min_size = 0.001
        if position_size < min_size:
            return 0

        return max(position_size, min_size)

    def next(self):
        """
        主要策略逻辑
        """
        if self.order:
            return

        # 处理买入信号
        if self.entry_sig[0] == 1:
            self._handle_entry_signal()

        # 处理卖出信号
        if self.position and self.sell_sig[0] == 1:
            self._handle_exit_signal()

    def _handle_entry_signal(self):
        """处理入场信号"""
        current_price = self.dataclose[0]
        size = self.calculate_position_size(current_price)

        if size > 0:
            self.log(
                f'买入信号 - 当前持仓: {self.position.size if self.position else 0}, '
                f'价格: {current_price:.2f}, 数量: {size:.8f}'
            )
            try:
                self.order = self.buy(size=size)
            except Exception as e:
                self.log(f'买入订单创建失败: {str(e)}', level='ERROR')
        else:
            self.log('买入信号触发但仓位计算为0，跳过交易')

    def _handle_exit_signal(self):
        """处理离场信号"""
        try:
            current_price = self.dataclose[0]
            sell_price = self.sell_price[0]

            self.log(
                f'卖出信号 - 持仓: {self.position.size}, '
                f'当前价格: {current_price:.2f}, 止损价: {sell_price:.2f}'
            )

            if current_price < sell_price:
                self.log('价格低于止损线，市价卖出')
                self.order = self.sell(
                    size=self.position.size,
                    exectype=bt.Order.Market
                )
            else:
                self.log('设置止损限价单')
                self.order = self.sell(
                    size=self.position.size,
                    exectype=bt.Order.Stop,
                    price=sell_price
                )
        except Exception as e:
            self.log(f'卖出订单创建失败: {str(e)}', level='ERROR')
