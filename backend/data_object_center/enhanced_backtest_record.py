from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json
from typing import List, Dict, Optional

from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class EnhancedBacktestRecord(Base):
    """增强回测记录"""
    __tablename__ = 'enhanced_backtest_record'

    # 基本信息
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 策略配置
    entry_strategy = Column(String(100), nullable=False, comment='入场策略')
    exit_strategy = Column(String(100), nullable=False, comment='出场策略')
    filter_strategy = Column(String(100), comment='过滤策略')
    
    # 交易配置
    symbols = Column(JSON, nullable=False, comment='交易对列表')
    timeframe = Column(String(20), nullable=False, comment='时间框架')
    backtest_period = Column(String(10), comment='回测时间段：1m/3m/1y')
    
    # 回测参数
    initial_cash = Column(Float, default=100000.0, comment='初始资金')
    risk_percent = Column(Float, default=2.0, comment='风险百分比')
    commission = Column(Float, default=0.001, comment='手续费率')
    
    # 状态信息
    status = Column(String(20), default='running', comment='状态：running/analyzing/completed/failed')
    error_message = Column(Text, comment='错误信息')
    
    # 时间信息
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 整体结果
    total_trades = Column(Integer, default=0, comment='总交易次数')
    winning_trades = Column(Integer, default=0, comment='获利次数')
    losing_trades = Column(Integer, default=0, comment='亏损次数')
    win_rate = Column(Float, default=0.0, comment='胜率')
    total_return = Column(Float, default=0.0, comment='总收益率')
    avg_win_profit = Column(Float, default=0.0, comment='平均盈利金额')
    avg_loss_profit = Column(Float, default=0.0, comment='平均亏损金额')
    profit_loss_ratio = Column(Float, default=0.0, comment='盈亏比')
    
    # 详细结果（JSON格式存储每个交易对的结果）
    symbol_results = Column(JSON, comment='各交易对详细结果')
    
    # 其他信息
    description = Column(Text, comment='描述')
    config_key = Column(String(100), comment='配置键')

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'entry_strategy': self.entry_strategy,
            'exit_strategy': self.exit_strategy,
            'filter_strategy': self.filter_strategy,
            'symbols': self.symbols,
            'timeframe': self.timeframe,
            'backtest_period': self.backtest_period,
            'initial_cash': self.initial_cash,
            'risk_percent': self.risk_percent,
            'commission': self.commission,
            'status': self.status,
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'total_return': self.total_return,
            'avg_win_profit': self.avg_win_profit,
            'avg_loss_profit': self.avg_loss_profit,
            'profit_loss_ratio': self.profit_loss_ratio,
            'symbol_results': self.symbol_results,
            'description': self.description,
            'config_key': self.config_key
        }

    @classmethod
    def create(cls, data: Dict) -> Optional['EnhancedBacktestRecord']:
        """创建新记录"""
        try:
            record = cls(**data)
            session.add(record)
            session.commit()
            return record
        except Exception as e:
            session.rollback()
            print(f"创建回测记录失败: {e}")
            return None

    @classmethod
    def get_by_id(cls, record_id: int) -> Optional['EnhancedBacktestRecord']:
        """根据ID获取记录"""
        try:
            return session.query(cls).filter(cls.id == record_id).first()
        except Exception as e:
            print(f"获取回测记录失败: {e}")
            return None

    @classmethod
    def list_all(cls, status: Optional[str] = None, limit: int = 100) -> List['EnhancedBacktestRecord']:
        """获取所有记录"""
        try:
            query = session.query(cls)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.created_at.desc()).limit(limit).all()
        except Exception as e:
            print(f"获取回测记录列表失败: {e}")
            return []

    @classmethod
    def update_status(cls, record_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """更新状态"""
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            if record:
                record.status = status
                record.error_message = error_message
                record.updated_at = datetime.now()
                if status == 'completed' or status == 'failed':
                    record.end_time = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"更新回测状态失败: {e}")
            return False

    @classmethod
    def update_results(cls, record_id: int, results: Dict) -> bool:
        """更新回测结果"""
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            if record:
                # 更新整体统计
                if 'total_trades' in results:
                    record.total_trades = results['total_trades']
                if 'winning_trades' in results:
                    record.winning_trades = results['winning_trades']
                if 'losing_trades' in results:
                    record.losing_trades = results['losing_trades']
                if 'win_rate' in results:
                    record.win_rate = results['win_rate']
                if 'total_return' in results:
                    record.total_return = results['total_return']
                if 'avg_win_profit' in results:
                    record.avg_win_profit = results['avg_win_profit']
                if 'avg_loss_profit' in results:
                    record.avg_loss_profit = results['avg_loss_profit']
                if 'profit_loss_ratio' in results:
                    record.profit_loss_ratio = results['profit_loss_ratio']
                if 'symbol_results' in results:
                    record.symbol_results = results['symbol_results']
                
                record.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"更新回测结果失败: {e}")
            return False

    @classmethod
    def delete_by_id(cls, record_id: int) -> bool:
        """删除记录"""
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"删除回测记录失败: {e}")
            return False

    @classmethod
    def get_summary_stats(cls) -> Dict:
        """获取汇总统计"""
        try:
            total_count = session.query(cls).count()
            running_count = session.query(cls).filter(cls.status == 'running').count()
            completed_count = session.query(cls).filter(cls.status == 'completed').count()
            failed_count = session.query(cls).filter(cls.status == 'failed').count()
            
            # 获取盈利策略数
            profitable_count = session.query(cls).filter(
                cls.status == 'completed',
                cls.total_return > 0
            ).count()
            
            # 获取最高胜率
            max_win_rate_record = session.query(cls).filter(
                cls.status == 'completed'
            ).order_by(cls.win_rate.desc()).first()
            
            max_win_rate = max_win_rate_record.win_rate if max_win_rate_record else 0.0
            
            return {
                'total_count': total_count,
                'running_count': running_count,
                'completed_count': completed_count,
                'failed_count': failed_count,
                'profitable_count': profitable_count,
                'max_win_rate': max_win_rate
            }
        except Exception as e:
            print(f"获取汇总统计失败: {e}")
            return {
                'total_count': 0,
                'running_count': 0,
                'completed_count': 0,
                'failed_count': 0,
                'profitable_count': 0,
                'max_win_rate': 0.0
            } 