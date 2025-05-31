from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import json


@dataclass
class BacktestConfig:
    """回测配置类"""
    # 策略配置
    entry_strategy: str  # 入场策略代码
    exit_strategy: str   # 出场策略代码
    symbols: List[str]  # 交易对列表
    timeframe: str      # 时间框架
    
    filter_strategy: Optional[str] = None  # 过滤策略代码（可选）
    initial_cash: float = 10000.0  # 初始资金
    risk_percent: float = 1.0      # 风险比例（百分比）
    commission: float = 0.001      # 手续费率
    start_date: Optional[str] = None  # 开始日期
    end_date: Optional[str] = None    # 结束日期
    description: Optional[str] = None  # 回测描述
    tags: List[str] = field(default_factory=list)  # 标签
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """初始化后的处理"""
        # 验证必填字段
        if not self.entry_strategy:
            raise ValueError("入场策略不能为空")
        if not self.exit_strategy:
            raise ValueError("出场策略不能为空")
        if not self.symbols:
            raise ValueError("交易对列表不能为空")
        if not self.timeframe:
            raise ValueError("时间框架不能为空")
            
        # 验证数值范围
        if self.initial_cash <= 0:
            raise ValueError("初始资金必须大于0")
        if not 0 < self.risk_percent <= 100:
            raise ValueError("风险比例必须在0-100之间")
        if not 0 <= self.commission <= 1:
            raise ValueError("手续费率必须在0-1之间")
            
        # 验证日期格式
        if self.start_date:
            try:
                datetime.strptime(self.start_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("开始日期格式无效，应为YYYY-MM-DD")
        if self.end_date:
            try:
                datetime.strptime(self.end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("结束日期格式无效，应为YYYY-MM-DD")
                
        # 验证日期范围
        if self.start_date and self.end_date:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            if start >= end:
                raise ValueError("开始日期必须早于结束日期")
    
    def generate_key(self) -> str:
        """生成配置的唯一键"""
        # 创建配置字典
        config_dict = {
            'entry_strategy': self.entry_strategy,
            'exit_strategy': self.exit_strategy,
            'filter_strategy': self.filter_strategy,
            'symbols': sorted(self.symbols),  # 排序以确保顺序一致
            'timeframe': self.timeframe,
            'initial_cash': self.initial_cash,
            'risk_percent': self.risk_percent,
            'commission': self.commission,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'parameters': self.parameters
        }
        
        # 转换为JSON字符串
        config_str = json.dumps(config_dict, sort_keys=True)
        
        # 生成MD5哈希
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        name_parts = [
            self.entry_strategy,
            self.exit_strategy
        ]
        if self.filter_strategy:
            name_parts.append(self.filter_strategy)
            
        return "/".join(name_parts)
    
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
            'description': self.description,
            'tags': self.tags,
            'parameters': self.parameters,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BacktestConfig':
        """从字典创建实例"""
        return cls(**data)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"BacktestConfig({self.get_display_name()})"


@dataclass
class BacktestResult:
    """单个交易对的回测结果"""
    config_key: str
    symbol: str
    initial_value: float
    final_value: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_amount: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    total_entry_signals: int
    total_sell_signals: int
    signal_execution_rate: float
    backtest_date: str
    duration_days: int
    
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
            'duration_days': self.duration_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BacktestResult':
        """从字典创建实例"""
        return cls(**data)


@dataclass
class BacktestSummary:
    """回测汇总结果"""
    config_key: str
    config: BacktestConfig
    total_symbols: int
    avg_return: float
    best_symbol: str
    worst_symbol: str
    best_return: float
    worst_return: float
    total_trades_all: int
    avg_win_rate: float
    avg_sharpe: float
    individual_results: List[BacktestResult]
    created_at: str
    
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BacktestSummary':
        """从字典创建实例"""
        # 转换配置
        config = BacktestConfig.from_dict(data['config'])
        
        # 转换单个结果
        individual_results = [
            BacktestResult.from_dict(r) for r in data['individual_results']
        ]
        
        return cls(
            config_key=data['config_key'],
            config=config,
            total_symbols=data['total_symbols'],
            avg_return=data['avg_return'],
            best_symbol=data['best_symbol'],
            worst_symbol=data['worst_symbol'],
            best_return=data['best_return'],
            worst_return=data['worst_return'],
            total_trades_all=data['total_trades_all'],
            avg_win_rate=data['avg_win_rate'],
            avg_sharpe=data['avg_sharpe'],
            individual_results=individual_results,
            created_at=data['created_at']
        ) 