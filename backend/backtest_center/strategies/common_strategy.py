from typing import Optional, Dict, Any
import backtrader as bt

from backend.backtest_center.strategies.base_strategy import BaseStrategy
from backend.backtest_center.utils.logger_config import setup_logger


class CommonStrategy(BaseStrategy):
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

        # 交易管理
        self.order = None
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.buy_price = None
        self.trade_records = []

        # 设置日志
        self.logger = setup_logger('backtest_system')

    def log(self, txt: str, dt: Optional[Any] = None, level: str = 'INFO') -> None:
        dt = dt or self.datas[0].datetime.date(0)
        msg = f'{dt.isoformat()} {txt}'
        if level == 'INFO':
            self.logger.info(msg)
        elif level == 'WARNING':
            self.logger.warning(msg)
        elif level == 'ERROR':
            self.logger.error(msg)

    def calculate_position_size(self, price: float) -> float:
        """
        计算交易规模

        Args:
            price: 当前价格

        Returns:
            float: 计算出的交易规模
        """
        # 计算每笔交易的资金量
        try:
            # 获取当前可用资金
            cash = self.broker.getcash()
            # 计算基于风险的交易金额
            trade_value = cash * (self.p.risk_percent / 100)
            # 计算当前投资组合总值
            portfolio_value = self.broker.getvalue()
            # 计算最大允许的仓位价值
            max_position_value = portfolio_value * self.p.max_position_size
            # 获取当前持仓价值
            current_position_value = self.position.size * price if self.position else 0
            # 计算剩余可用仓位价值
            available_position_value = max_position_value - current_position_value
            # 确定最终的交易金额
            final_trade_value = min(trade_value, available_position_value)
            # 如果可用金额太小，返回0
            if final_trade_value < price * 0.001:  # 最小交易单位
                self.log(f"计算的交易金额 {final_trade_value:.2f} 太小，跳过交易", level='WARNING')
                return 0
            # 计算最终的交易数量
            position_size = final_trade_value / price
            # 记录详细的计算过程
            self.log(f"仓位计算 - 可用资金: {cash:.2f}, 计划交易金额: {trade_value:.2f}, "
                     f"最大允许仓位: {max_position_value:.2f}, 当前持仓: {current_position_value:.2f}, "
                     f"最终交易数量: {position_size:.8f}")

            return position_size

        except Exception as e:
            self.log(f"仓位计算错误: {str(e)}", level='ERROR')
            return 0

    def notify_order(self, order):
        """
        改进的订单通知处理
        """
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            if order.isbuy():
                self.log(f'买入执行 - 价格: {order.executed.price:.2f}, '
                         f'数量: {order.executed.size:.8f}, '
                         f'金额: {order.executed.value:.2f}, '
                         f'手续费: {order.executed.comm:.2f}')
                self.buy_price = order.executed.price
            else:
                self.log(f'卖出执行 - 价格: {order.executed.price:.2f}, '
                         f'数量: {order.executed.size:.8f}, '
                         f'金额: {order.executed.value:.2f}, '
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

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单失败 - 状态: {order.status}', level='WARNING')
        # 重置订单
        self.order = None

    def next(self):
        """
        主要策略逻辑
        """
        if self.order:
            return

        # 处理买入信号, 支持加仓
        if self.entry_sig[0] == 1:
            self._handle_entry_signal()

        if self.entry_price[0] != 1 and self.sell_sig[0] != 1 and self.position:
            self._handle_stop_loss_price()

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
                self.order = self.sell(size=self.position.size)
            else:
                self.log('设置止损限价单')
                self.order = self.sell(size=self.position.size,
                                       exectype=bt.Order.Stop,
                                       price=sell_price)
        except Exception as e:
            self.log(f'卖出订单创建失败: {str(e)}', level='ERROR')

    # def _handle_stop_loss_price(self):
    #     try:
    #         sell_price = self.sell_price[0]
    #         self.log('设置止损限价单')
    #         self.order = self.sell(size=self.position.size,
    #                                exectype=bt.Order.Stop,
    #                                price=sell_price)
    #     except Exception as e:
    #         self.log(f'止损订单创建失败: {str(e)}', level='ERROR')
