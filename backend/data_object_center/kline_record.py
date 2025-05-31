from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List

from backend._utils import DatabaseUtils, LogConfig

Base = declarative_base()
logger = LogConfig.get_logger(__name__)

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

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def bulk_upsert(session: Session, records: List['KlineRecord']) -> bool:
        """批量插入或更新"""
        try:
            for record in records:
                session.merge(record)
            return True
        except Exception as e:
            logger.error(f"批量更新K线记录失败: {e}")
            raise

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def get_by_symbol_timeframe(session: Session, symbol: str, timeframe: str, start_time: datetime = None, end_time: datetime = None) -> List['KlineRecord']:
        """根据交易对和时间框架获取K线记录"""
        query = session.query(KlineRecord).filter(
            KlineRecord.symbol == symbol,
            KlineRecord.timeframe == timeframe
        )
        
        if start_time:
            query = query.filter(KlineRecord.datetime >= start_time)
        if end_time:
            query = query.filter(KlineRecord.datetime <= end_time)
            
        return query.order_by(KlineRecord.datetime).all()

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def delete_by_symbol_timeframe(session: Session, symbol: str, timeframe: str) -> bool:
        """删除指定交易对和时间框架的K线记录"""
        try:
            session.query(KlineRecord).filter(
                KlineRecord.symbol == symbol,
                KlineRecord.timeframe == timeframe
            ).delete()
            return True
        except Exception as e:
            logger.error(f"删除K线记录失败: {e}")
            raise

# 在模块导入时自动创建表
engine = DatabaseUtils.get_engine()
Base.metadata.create_all(bind=engine) 