from sqlalchemy import Column, Integer, String, delete, select, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import List, Optional, TYPE_CHECKING

from backend._utils import DatabaseUtils, LogConfig

Base = declarative_base()
logger = LogConfig.get_logger(__name__)

if TYPE_CHECKING:
    from typing import TypeVar
    BacktestRecordType = TypeVar('BacktestRecordType', bound='BacktestRecord')

class BacktestRecord(Base):
    __tablename__ = 'backtest_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    back_test_result_key = Column(String, comment='回测结果FK')
    transaction_time = Column(String, comment='交易时间')
    transaction_result = Column(String, comment='交易结果')
    transaction_pnl = Column(Float(precision=2), comment='交易收益')

    def to_dict(self):
        return {
            'id': self.id,
            'back_test_result_key': self.back_test_result_key,
            'transaction_time': self.transaction_time,
            'transaction_result': self.transaction_result,
            'transaction_pnl': self.transaction_pnl
        }

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def list_all(session: Session) -> List[dict]:
        """获取所有回测记录"""
        stmt = select(BacktestRecord)
        records = session.execute(stmt).scalars().all()
        return [record.to_dict() for record in records]

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def list_by_key(session: Session, back_test_result_key: str) -> List[dict]:
        """根据回测结果键获取回测记录"""
        stmt = select(BacktestRecord).where(BacktestRecord.back_test_result_key == back_test_result_key)
        records = session.execute(stmt).scalars().all()
        return [record.to_dict() for record in records]

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def get_by_id(session: Session, id: int) -> Optional['BacktestRecord']:
        """根据ID获取回测记录"""
        stmt = select(BacktestRecord).where(BacktestRecord.id == id)
        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def bulk_insert(session: Session, records: List[dict]) -> bool:
        """批量插入回测记录"""
        try:
            for record_data in records:
                record = BacktestRecord(**record_data)
                session.add(record)
            return True
        except Exception as e:
            logger.error(f"批量插入回测记录失败: {e}")
            raise

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def delete_by_key(session: Session, back_test_result_key: str) -> bool:
        """删除指定回测结果键的记录"""
        try:
            stmt = delete(BacktestRecord).where(BacktestRecord.back_test_result_key == back_test_result_key)
            session.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"删除回测记录失败: {e}")
            raise

if __name__ == '__main__':
    BacktestRecord.delete_all()
