from datetime import datetime
from typing import Optional, Dict, List
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EnhancedBacktestDetail(Base):
    """增强回测明细"""
    __tablename__ = 'enhanced_backtest_details'
    
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    position_size = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    profit_percent = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    net_profit = Column(Float, nullable=False)
    net_profit_percent = Column(Float, nullable=False)
    entry_reason = Column(String(500))
    exit_reason = Column(String(500))
    
    def __init__(self,
                 record_id: int,
                 symbol: str,
                 entry_time: datetime,
                 exit_time: datetime,
                 entry_price: float,
                 exit_price: float,
                 position_size: float,
                 profit: float,
                 profit_percent: float,
                 commission: float,
                 net_profit: float,
                 net_profit_percent: float,
                 entry_reason: Optional[str] = None,
                 exit_reason: Optional[str] = None):
        self.record_id = record_id
        self.symbol = symbol
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.position_size = position_size
        self.profit = profit
        self.profit_percent = profit_percent
        self.commission = commission
        self.net_profit = net_profit
        self.net_profit_percent = net_profit_percent
        self.entry_reason = entry_reason
        self.exit_reason = exit_reason
    
    @classmethod
    def create(cls, data: Dict) -> 'EnhancedBacktestDetail':
        """创建回测明细"""
        from sqlalchemy.orm import Session
        from backend.database import get_db
        
        session = Session(get_db())
        try:
            detail = cls(
                record_id=data['record_id'],
                symbol=data['symbol'],
                entry_time=datetime.fromisoformat(data['entry_time']),
                exit_time=datetime.fromisoformat(data['exit_time']),
                entry_price=data['entry_price'],
                exit_price=data['exit_price'],
                position_size=data['position_size'],
                profit=data['profit'],
                profit_percent=data['profit_percent'],
                commission=data['commission'],
                net_profit=data['net_profit'],
                net_profit_percent=data['net_profit_percent'],
                entry_reason=data.get('entry_reason'),
                exit_reason=data.get('exit_reason')
            )
            session.add(detail)
            session.commit()
            return detail
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_by_record_id(cls, record_id: int) -> List['EnhancedBacktestDetail']:
        """根据记录ID获取回测明细"""
        from sqlalchemy.orm import Session
        from backend.database import get_db
        
        session = Session(get_db())
        try:
            return session.query(cls).filter(cls.record_id == record_id).all()
        finally:
            session.close()
    
    def save(self):
        """保存回测明细"""
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
            'symbol': self.symbol,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat(),
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'position_size': self.position_size,
            'profit': self.profit,
            'profit_percent': self.profit_percent,
            'commission': self.commission,
            'net_profit': self.net_profit,
            'net_profit_percent': self.net_profit_percent,
            'entry_reason': self.entry_reason,
            'exit_reason': self.exit_reason
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict()) 