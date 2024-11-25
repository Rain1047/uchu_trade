# models/backtest_result.py
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class BacktestResults:
    """回测结果数据类"""
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
        try:
            return (
                f"\n=== 回测结果 ===\n"
                f"初始投资金额: ${self.initial_value:.2f}\n"
                f"最终投资金额: ${self.final_value:.2f}\n"
                f"总收益率: {self.total_return*100:.2f}%\n"  # 确保是百分比格式
                f"年化收益率: {self.annual_return*100:.2f}%\n"  # 确保是百分比格式
                f"夏普比率: {self.sharpe_ratio:.3f if self.sharpe_ratio else 'N/A'}\n"
                f"最大回撤: {self.max_drawdown*100:.2f}%\n"  # 确保是百分比格式
                f"最大回撤金额: ${self.max_drawdown_amount:.2f}\n"
                f"\n=== 交易统计 ===\n"
                f"总交易次数: {self.total_trades}\n"
                f"盈利交易次数: {self.winning_trades}\n"
                f"亏损交易次数: {self.losing_trades}\n"
                f"胜率: {self.win_rate:.2f}%\n"
                f"平均盈利: ${self.avg_win:.2f if self.winning_trades > 0 else 0:.2f}\n"
                f"平均亏损: ${self.avg_loss:.2f if self.losing_trades > 0 else 0:.2f}"
            )
        except Exception as e:
            logger.error(f"格式化回测结果时出错: {str(e)}")
            return "回测结果格式化失败"
