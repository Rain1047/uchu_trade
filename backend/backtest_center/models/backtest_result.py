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

    def format_percentage(self, value: float) -> str:
        """格式化百分比值"""
        try:
            logger.debug(f"格式化百分比值, 输入值: {value}, 类型: {type(value)}")
            formatted = f"{float(value) * 100:.2f}%"
            logger.debug(f"格式化后的结果: {formatted}")
            return formatted
        except Exception as e:
            logger.error(f"格式化百分比失败, 值: {value}, 错误: {str(e)}")
            return "N/A"

    def format_currency(self, value: float) -> str:
        """格式化货币值"""
        try:
            logger.debug(f"格式化货币值, 输入值: {value}, 类型: {type(value)}")
            formatted = f"${float(value):.2f}"
            logger.debug(f"格式化后的结果: {formatted}")
            return formatted
        except Exception as e:
            logger.error(f"格式化货币失败, 值: {value}, 错误: {str(e)}")
            return "N/A"

    def __str__(self) -> str:
        """返回可读性好的字符串表示"""
        try:
            # 记录所有属性的值和类型
            logger.debug("开始格式化回测结果，属性值如下：")
            for attr_name, attr_value in self.__dict__.items():
                logger.debug(f"{attr_name}: 值={attr_value}, 类型={type(attr_value)}")

            lines = [
                "=== 回测结果 ===",
                f"初始投资金额: {self.format_currency(self.initial_value)}",
                f"最终投资金额: {self.format_currency(self.final_value)}",
                f"总收益率: {self.format_percentage(self.total_return)}",
                f"年化收益率: {self.format_percentage(self.annual_return)}",
            ]

            # 分开处理夏普比率
            if self.sharpe_ratio is not None:
                try:
                    lines.append(f"夏普比率: {float(self.sharpe_ratio):.3f}")
                except Exception as e:
                    logger.error(f"格式化夏普比率失败: {str(e)}")
                    lines.append("夏普比率: N/A")
            else:
                lines.append("夏普比率: N/A")

            lines.extend([
                f"最大回撤: {self.format_percentage(self.max_drawdown)}",
                f"最大回撤金额: {self.format_currency(self.max_drawdown_amount)}",
                "",
                "=== 交易统计 ===",
                f"总交易次数: {self.total_trades}",
                f"盈利交易次数: {self.winning_trades}",
                f"亏损交易次数: {self.losing_trades}",
            ])

            # 分开处理胜率
            try:
                logger.debug(f"处理胜率，原始值: {self.win_rate}")
                win_rate_value = float(self.win_rate) / 100  # 因为已经是百分比
                lines.append(f"胜率: {self.format_percentage(win_rate_value)}")
            except Exception as e:
                logger.error(f"格式化胜率失败: {str(e)}")
                lines.append("胜率: N/A")

            # 分开处理平均盈亏
            if self.winning_trades > 0:
                lines.append(f"平均盈利: {self.format_currency(self.avg_win)}")
            else:
                lines.append("平均盈利: N/A")

            if self.losing_trades > 0:
                lines.append(f"平均亏损: {self.format_currency(self.avg_loss)}")
            else:
                lines.append("平均亏损: N/A")

            result = "\n".join(lines)
            logger.debug(f"最终格式化结果:\n{result}")
            return result

        except Exception as e:
            logger.error(f"格式化回测结果时出错: {str(e)}", exc_info=True)
            return "回测结果格式化失败"
