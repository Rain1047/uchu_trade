from pydantic import BaseModel
from typing import Optional


class StrategyExecuteResult:
    # 交易对
    symbol: Optional[str] = ''
    # 买入方向
    side: Optional[str] = None
    # 持仓方向
    pos_side: Optional[str] = None
    # 买入信号
    signal: Optional[bool] = False
    # 买入价格
    entry_price: Optional[str] = ''
    # 止盈价格
    profit_price: Optional[str] = ''
    # 止损价格
    stop_loss_price: Optional[str] = ''
    # 离场价格
    exit_price: Optional[str] = ''
    # 买入仓位
    sz: Optional[str] = ''
    # USDT仓位
    sz_usdt: Optional[str] = ''
    # 交易实例id
    st_inst_id: Optional[int] = None
    # 交易间隔
    interval: Optional[str] = ''

    def to_dict(self) -> dict:
        """
        Convert strategy execute result to dictionary
        Returns:
            dict: Dictionary representation of the strategy execute result
        """
        return {
            'symbol': self.symbol,
            'side': self.side,
            'pos_side': self.pos_side,
            'signal': self.signal,
            'entry_price': self.entry_price,
            'profit_price': self.profit_price,
            'stop_loss_price': self.stop_loss_price,
            'exit_price': self.exit_price,
            'sz': self.sz,
            'sz_usdt': self.sz_usdt,
            'st_inst_id': self.st_inst_id,
            'interval': self.interval
        }




