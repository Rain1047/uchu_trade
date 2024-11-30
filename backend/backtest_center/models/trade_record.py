from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TradeRecord:
    """
    交易记录数据类，记录单次交易的所有相关信息

    Attributes:
        datetime (str): 交易时间
        action (str): 交易动作 ('BUY' or 'SELL')
        price (float): 交易价格
        size (float): 交易数量
        value (float): 交易金额
        commission (float): 手续费
        pnl (float): 收益（仅在卖出时有效）
    """
    datetime: str
    action: str
    price: float
    size: float
    value: float
    commission: float
    pnl: float = 0.0

    def to_dict(self) -> dict:
        """转换为字典格式，便于导出到DataFrame"""
        return {
            'datetime': self.datetime,
            'action': self.action,
            'price': self.price,
            'size': self.size,
            'value': self.value,
            'commission': self.commission,
            'pnl': self.pnl
        }

    @property
    def formatted_datetime(self) -> str:
        """返回格式化的日期时间字符串"""
        return datetime.strptime(self.datetime, '%Y-%m-%d').strftime('%Y-%m-%d')

    def __str__(self) -> str:
        """返回可读性好的字符串表示"""
        return (
            f"交易记录 [{self.formatted_datetime}]\n"
            f"动作: {self.action}\n"
            f"价格: {self.price:.2f}\n"
            f"数量: {self.size:.8f}\n"
            f"金额: {self.value:.2f}\n"
            f"手续费: {self.commission:.2f}\n"
            f"收益: {self.pnl:.2f if self.action == 'SELL' else 'N/A'}"
        )