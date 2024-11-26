import backtrader as bt
from typing import Optional, Any, Dict
from datetime import datetime
import logging

from backend.backtest_center.utils.logger_config import setup_logger


class BaseStrategy(bt.Strategy):
    """
    基础策略类，提供通用的功能和接口

    主要功能：
    - 日志记录
    - 基础的仓位管理
    - 订单管理的基础设施
    - 交易记录的基础设施
    """

    def __init__(self):
        """初始化策略基类"""
        self.order = None  # 当前挂单
        self.orders = []  # 订单历史
        self.trade_count = 0  # 交易次数
        self.winning_trades = 0  # 盈利交易数
        self.losing_trades = 0  # 亏损交易数
        # 设置日志
        self.logger = setup_logger(self.__class__.__name__)

    def _setup_logging(self):
        """设置日志配置"""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log(self, txt: str, dt: Optional[Any] = None, level: str = 'INFO') -> None:
        """
        记录日志

        Args:
            txt: 日志内容
            dt: 日期时间，默认为当前K线的时间
            level: 日志级别
        """
        dt = dt or self.datas[0].datetime.date(0)
        message = f'{dt.isoformat()} {txt}'

        log_levels = {
            'DEBUG': self.logger.debug,
            'INFO': self.logger.info,
            'WARNING': self.logger.warning,
            'ERROR': self.logger.error
        }
        log_levels.get(level, self.logger.info)(message)

    def calculate_position_size(self, price: float, risk_amount: float) -> float:
        """
        计算持仓规模

        Args:
            price: 当前价格
            risk_amount: 计划使用的资金量

        Returns:
            float: 计算出的持仓规模
        """
        raise NotImplementedError("子类必须实现仓位计算方法")

    def get_position_value(self) -> float:
        """获取当前持仓市值"""
        return self.position.size * self.data.close[0] if self.position else 0

    def get_portfolio_stats(self) -> Dict:
        """
        获取投资组合统计数据

        Returns:
            Dict: 包含各种统计指标的字典
        """
        return {
            'cash': self.broker.getcash(),
            'value': self.broker.getvalue(),
            'position': self.position.size if self.position else 0,
            'position_value': self.get_position_value(),
        }

    def notify_order(self, order):
        """
        订单状态更新通知

        Args:
            order: 订单对象
        """
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self.log(
                f'订单执行: {order.executed.price:.2f}, '
                f'数量: {order.executed.size:.8f}, '
                f'价值: {order.executed.value:.2f}, '
                f'手续费: {order.executed.comm:.2f}',
                level='INFO'
            )
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单失败 - 状态: {order.status}', level='WARNING')

        # 重置订单
        if not order.alive():
            self.order = None

    def notify_trade(self, trade):
        """
        交易完成通知

        Args:
            trade: 交易对象
        """
        if not trade.isclosed:
            return

        self.trade_count += 1
        if trade.pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        self.log(
            f'交易完成 - 毛利润: {trade.pnl:.2f}, '
            f'净利润: {trade.pnlcomm:.2f}',
            level='INFO'
        )

    def should_cancel_order(self, order) -> bool:
        """
        判断是否应该取消订单

        Args:
            order: 订单对象

        Returns:
            bool: 是否应该取消订单
        """
        return False  # 默认不取消订单，子类可以重写这个方法

    def next(self):
        """
        K线更新时的操作，子类必须实现这个方法
        """
        raise NotImplementedError("子类必须实现next方法")

    def stop(self):
        """
        策略结束时的操作
        """
        win_rate = (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0
        self.log(
            f'策略结束 - 总交易: {self.trade_count}, '
            f'盈利: {self.winning_trades}, '
            f'亏损: {self.losing_trades}, '
            f'胜率: {win_rate:.2f}%',
            level='INFO'
        )