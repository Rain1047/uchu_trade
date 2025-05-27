from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import json


@dataclass
class BacktestConfig:
    """回测配置类 - 支持灵活的策略组合"""
    
    # 策略配置
    entry_strategy: str  # 入场策略名称
    exit_strategy: str   # 出场策略名称
    filter_strategy: Optional[str] = None  # 过滤策略名称（可选）
    
    # 交易配置
    symbols: List[str] = field(default_factory=list)  # 交易对列表，支持多选
    timeframe: str = "1h"  # 时间窗口
    
    # 回测参数
    initial_cash: float = 100000.0  # 初始资金
    risk_percent: float = 2.0  # 风险百分比
    commission: float = 0.001  # 手续费
    
    # 时间范围
    start_date: Optional[str] = None  # 开始日期 YYYY-MM-DD
    end_date: Optional[str] = None    # 结束日期 YYYY-MM-DD
    
    # 策略参数（可选）
    strategy_params: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    created_at: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def generate_key(self) -> str:
        """生成唯一的配置键"""
        # 创建配置的哈希值作为唯一标识
        config_dict = {
            'entry_strategy': self.entry_strategy,
            'exit_strategy': self.exit_strategy,
            'filter_strategy': self.filter_strategy,
            'symbols': sorted(self.symbols),  # 排序确保一致性
            'timeframe': self.timeframe,
            'strategy_params': self.strategy_params
        }
        
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:12]
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        symbols_str = "+".join(self.symbols[:3])  # 最多显示3个交易对
        if len(self.symbols) > 3:
            symbols_str += f"+{len(self.symbols)-3}more"
        
        filter_part = f"_F{self.filter_strategy}" if self.filter_strategy else ""
        
        return f"E{self.entry_strategy}_X{self.exit_strategy}{filter_part}_{symbols_str}_{self.timeframe}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'entry_strategy': self.entry_strategy,
            'exit_strategy': self.exit_strategy,
            'filter_strategy': self.filter_strategy,
            'symbols': self.symbols,
            'timeframe': self.timeframe,
            'initial_cash': self.initial_cash,
            'risk_percent': self.risk_percent,
            'commission': self.commission,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'strategy_params': self.strategy_params,
            'created_at': self.created_at,
            'description': self.description,
            'key': self.generate_key(),
            'display_name': self.get_display_name()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BacktestConfig':
        """从字典创建实例"""
        # 移除不属于构造函数的字段
        data_copy = data.copy()
        data_copy.pop('key', None)
        data_copy.pop('display_name', None)
        
        return cls(**data_copy)


@dataclass
class BacktestResult:
    """回测结果类"""
    
    config_key: str  # 对应的配置键
    symbol: str      # 单个交易对的结果
    
    # 基础指标
    initial_value: float
    final_value: float
    total_return: float
    annual_return: float
    
    # 风险指标
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_amount: float
    
    # 交易统计
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    
    # 信号统计
    total_entry_signals: int
    total_sell_signals: int
    signal_execution_rate: float  # 信号执行率
    
    # 时间信息
    backtest_date: str
    duration_days: int
    
    # 额外信息
    notes: Optional[str] = None
    
    def __post_init__(self):
        if not hasattr(self, 'backtest_date') or self.backtest_date is None:
            self.backtest_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'config_key': self.config_key,
            'symbol': self.symbol,
            'initial_value': self.initial_value,
            'final_value': self.final_value,
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_amount': self.max_drawdown_amount,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'total_entry_signals': self.total_entry_signals,
            'total_sell_signals': self.total_sell_signals,
            'signal_execution_rate': self.signal_execution_rate,
            'backtest_date': self.backtest_date,
            'duration_days': self.duration_days,
            'notes': self.notes
        }


@dataclass
class BacktestSummary:
    """多交易对回测汇总结果"""
    
    config_key: str
    config: BacktestConfig
    
    # 汇总指标
    total_symbols: int
    avg_return: float
    best_symbol: str
    worst_symbol: str
    best_return: float
    worst_return: float
    
    # 整体统计
    total_trades_all: int
    avg_win_rate: float
    avg_sharpe: float
    
    # 个别结果
    individual_results: List[BacktestResult]
    
    # 时间信息
    created_at: str
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'config_key': self.config_key,
            'config': self.config.to_dict(),
            'total_symbols': self.total_symbols,
            'avg_return': self.avg_return,
            'best_symbol': self.best_symbol,
            'worst_symbol': self.worst_symbol,
            'best_return': self.best_return,
            'worst_return': self.worst_return,
            'total_trades_all': self.total_trades_all,
            'avg_win_rate': self.avg_win_rate,
            'avg_sharpe': self.avg_sharpe,
            'individual_results': [r.to_dict() for r in self.individual_results],
            'created_at': self.created_at
        } 