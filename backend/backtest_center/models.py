from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class BacktestResult:
    """单个交易对的回测结果"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    winning_pnl: float
    losing_pnl: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    trades: List[Dict]
    equity_curve: List[Dict]

@dataclass
class BacktestSummary:
    """回测汇总结果"""
    config_key: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    winning_pnl: float
    losing_pnl: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    individual_results: Dict[str, BacktestResult]
    created_at: datetime = datetime.now()

@dataclass
class BacktestConfig:
    """回测配置"""
    entry_strategy: str
    exit_strategy: str
    filter_strategy: Optional[str]
    symbols: List[str]
    timeframe: str
    initial_cash: float
    risk_percent: float
    commission: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str = "增强回测"
    
    def generate_key(self) -> str:
        """生成配置键"""
        key_parts = [
            self.entry_strategy,
            self.exit_strategy,
            self.filter_strategy or "no_filter",
            "_".join(sorted(self.symbols)),
            self.timeframe,
            f"cash{self.initial_cash}",
            f"risk{self.risk_percent}",
            f"comm{self.commission}"
        ]
        return "_".join(key_parts) 