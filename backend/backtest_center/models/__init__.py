from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class SymbolResult:
    """单个交易对的回测结果"""
    symbol: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    total_entry_signals: int
    total_sell_signals: int
    signal_execution_rate: float
    duration_days: int
    trades: List[Dict]  # 详细交易记录

@dataclass
class BacktestSummary:
    """回测结果汇总"""
    config_key: str
    total_symbols: int
    total_trades_all: int
    avg_return: float
    avg_win_rate: float
    avg_sharpe: float
    best_symbol: Optional[str]
    best_return: float
    worst_symbol: Optional[str]
    worst_return: float
    individual_results: List[SymbolResult]
    created_at: datetime = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'config_key': self.config_key,
            'total_symbols': self.total_symbols,
            'total_trades_all': self.total_trades_all,
            'avg_return': self.avg_return,
            'avg_win_rate': self.avg_win_rate,
            'avg_sharpe': self.avg_sharpe,
            'best_symbol': self.best_symbol,
            'best_return': self.best_return,
            'worst_symbol': self.worst_symbol,
            'worst_return': self.worst_return,
            'individual_results': [
                {
                    'symbol': r.symbol,
                    'total_trades': r.total_trades,
                    'winning_trades': r.winning_trades,
                    'losing_trades': r.losing_trades,
                    'win_rate': r.win_rate,
                    'total_return': r.total_return,
                    'annual_return': r.annual_return,
                    'sharpe_ratio': r.sharpe_ratio,
                    'max_drawdown': r.max_drawdown,
                    'total_entry_signals': r.total_entry_signals,
                    'total_sell_signals': r.total_sell_signals,
                    'signal_execution_rate': r.signal_execution_rate,
                    'duration_days': r.duration_days,
                    'trades': r.trades
                }
                for r in self.individual_results
            ],
            'created_at': self.created_at.isoformat()
        }

@dataclass
class BacktestConfig:
    """回测配置"""
    entry_strategy: str
    exit_strategy: str
    filter_strategy: Optional[str]
    symbols: List[str]
    timeframe: str
    backtest_period: str
    initial_cash: float
    risk_percent: float
    commission: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    save_to_db: bool = True
    description: str = "增强回测"
    created_at: datetime = datetime.now()
    
    def generate_key(self) -> str:
        """生成配置键"""
        key_parts = [
            self.entry_strategy,
            self.exit_strategy,
            self.filter_strategy if self.filter_strategy else "no_filter",
            "_".join(sorted(self.symbols)),
            self.timeframe,
            self.backtest_period,
            f"cash{self.initial_cash}",
            f"risk{self.risk_percent}",
            f"fee{self.commission}"
        ]
        return "_".join(key_parts)
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return f"{self.entry_strategy} + {self.exit_strategy}" + \
               (f" + {self.filter_strategy}" if self.filter_strategy else "")

__all__ = ['BacktestConfig', 'BacktestSummary', 'SymbolResult']
