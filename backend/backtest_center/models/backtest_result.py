from dataclasses import dataclass
from typing import Optional


@dataclass
class BacktestResults:
    """
    回测结果数据类，存储回测的所有关键指标

    Attributes:
        initial_value (float): 初始投资金额
        final_value (float): 最终投资组合价值
        total_return (float): 总收益率
        annual_return (float): 年化收益率
        sharpe_ratio (float): 夏普比率
        max_drawdown (float): 最大回撤百分比
        max_drawdown_amount (float): 最大回撤金额
        total_trades (int): 总交易次数
        winning_trades (int): 盈利交易次数
        losing_trades (int): 亏损交易次数
        avg_win (float): 平均盈利
        avg_loss (float): 平均亏损
        win_rate (float): 胜率
    """
    initial_value: float
    final_value: float
    total_return: float
    annual_return: float
    sharpe_ratio: Optional[float]
    max_drawdown: float
    max_drawdown_amount: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    win_rate: float

    def __str__(self) -> str:
        """返回可读性好的字符串表示"""
        return (
            f"\n=== 回测结果 ===\n"
            f"初始投资金额: ${self.initial_value:.2f}\n"
            f"最终投资金额: ${self.final_value:.2f}\n"
            f"总收益率: {self.total_return:.2%}\n"
            f"年化收益率: {self.annual_return:.2%}\n"
            f"夏普比率: {self.sharpe_ratio:.3f if self.sharpe_ratio else 'N/A'}\n"
            f"最大回撤: {self.max_drawdown:.2%}\n"
            f"最大回撤金额: ${self.max_drawdown_amount:.2f}\n"
            f"\n=== 交易统计 ===\n"
            f"总交易次数: {self.total_trades}\n"
            f"盈利交易次数: {self.winning_trades}\n"
            f"亏损交易次数: {self.losing_trades}\n"
            f"胜率: {self.win_rate:.2f}%\n"
            f"平均盈利: ${self.avg_win:.2f}\n"
            f"平均亏损: ${self.avg_loss:.2f}"
        )