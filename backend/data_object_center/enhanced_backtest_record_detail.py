from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from backend._utils import DatabaseUtils

Base = declarative_base()

class EnhancedBacktestRecordDetail(Base):
    """单交易对回测结果详情"""
    __tablename__ = 'enhanced_backtest_record_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False)

    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    profit_loss_ratio = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)

    # 交易记录 json
    trade_records = Column(JSON)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint('record_id', 'symbol', name='uix_record_symbol'),
        Index('idx_record_symbol', 'record_id', 'symbol'),
    )

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'symbol': self.symbol,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'total_profit': self.total_profit,
            'total_return': self.total_return,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'profit_loss_ratio': self.profit_loss_ratio,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'trade_records': self.trade_records,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def upsert(cls, session, data: dict):
        obj = session.query(cls).filter_by(record_id=data['record_id'], symbol=data['symbol']).first()
        if obj:
            for k,v in data.items():
                setattr(obj,k,v)
            obj.updated_at=datetime.now()
        else:
            obj = cls(**data)
            session.add(obj)
        session.commit()

    @classmethod
    def list_by_record(cls, session, record_id:int):
        return session.query(cls).filter_by(record_id=record_id).all()

# create table
engine = DatabaseUtils.get_engine()
Base.metadata.create_all(bind=engine) 