from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from backend._utils import DatabaseUtils

Base = declarative_base()

class KlineRecord(Base):
    """K线记录表"""
    __tablename__ = 'kline_record'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'datetime', name='uix_sym_tf_dt'),
        Index('idx_sym_tf_dt', 'symbol', 'timeframe', 'datetime'),
    )

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'datetime': self.datetime,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }

    @classmethod
    def bulk_upsert(cls, session, records):
        """批量插入或更新"""
        # 利用 SQLite "INSERT OR REPLACE" 语法
        for r in records:
            session.merge(r)
        session.commit()

# 在模块导入时自动创建表
engine = DatabaseUtils.get_engine()
Base.metadata.create_all(bind=engine) 