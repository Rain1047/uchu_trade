from datetime import datetime
from typing import Optional, Dict, List
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EnhancedBacktestResult(Base):
    """增强回测结果"""
    __tablename__ = 'enhanced_backtest_results'
    
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey('enhanced_backtest_records.id'), nullable=False)
    config_key = Column(String(100), nullable=False)
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)
    total_pnl = Column(Float, nullable=False)
    winning_pnl = Column(Float, nullable=False)
    losing_pnl = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    individual_results = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    def __init__(self,
                 record_id: int,
                 config_key: str,
                 total_trades: int,
                 winning_trades: int,
                 losing_trades: int,
                 total_pnl: float,
                 winning_pnl: float,
                 losing_pnl: float,
                 win_rate: float,
                 profit_factor: float,
                 max_drawdown: float,
                 individual_results: Dict[str, Dict],
                 created_at: datetime):
        self.record_id = record_id
        self.config_key = config_key
        self.total_trades = total_trades
        self.winning_trades = winning_trades
        self.losing_trades = losing_trades
        self.total_pnl = total_pnl
        self.winning_pnl = winning_pnl
        self.losing_pnl = losing_pnl
        self.win_rate = win_rate
        self.profit_factor = profit_factor
        self.max_drawdown = max_drawdown
        self.individual_results = individual_results
        self.created_at = created_at
    
    @classmethod
    def create(cls, data: Dict) -> 'EnhancedBacktestResult':
        """创建回测结果"""
        from sqlalchemy.orm import Session
        from backend.database import get_db
        
        session = Session(get_db())
        try:
            result = cls(
                record_id=data['record_id'],
                config_key=data['config_key'],
                total_trades=data['total_trades'],
                winning_trades=data['winning_trades'],
                losing_trades=data['losing_trades'],
                total_pnl=data['total_pnl'],
                winning_pnl=data['winning_pnl'],
                losing_pnl=data['losing_pnl'],
                win_rate=data['win_rate'],
                profit_factor=data['profit_factor'],
                max_drawdown=data['max_drawdown'],
                individual_results=data['individual_results'],
                created_at=datetime.now()
            )
            session.add(result)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_by_record_id(cls, record_id: int) -> Optional['EnhancedBacktestResult']:
        """根据记录ID获取回测结果"""
        from sqlalchemy.orm import Session
        from backend.database import get_db
        
        session = Session(get_db())
        try:
            return session.query(cls).filter(cls.record_id == record_id).first()
        finally:
            session.close()
    
    def save(self):
        """保存回测结果"""
        from sqlalchemy.orm import Session
        from backend.database import get_db
        
        session = Session(get_db())
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'record_id': self.record_id,
            'config_key': self.config_key,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': self.total_pnl,
            'winning_pnl': self.winning_pnl,
            'losing_pnl': self.losing_pnl,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'individual_results': self.individual_results,
            'created_at': self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict()) 