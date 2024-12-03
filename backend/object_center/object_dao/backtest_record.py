from sqlalchemy import Column, Integer, String, delete, select, Float
from sqlalchemy.ext.declarative import declarative_base

from backend.utils.utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


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

    @classmethod
    def list_all(cls):
        stmt = select(cls)
        return [record.to_dict() for record in stmt]

    @classmethod
    def list_by_key(cls, back_test_result_key: str) -> list:
        stmt = select(cls).where(cls.back_test_result_key == back_test_result_key)
        records = session.execute(stmt).scalars().all()
        return [record.to_dict() for record in records]

    @classmethod
    def get_by_id(cls, id: int):
        stmt = select(cls).where(cls.id == id)
        return session.execute(stmt).scalar_one_or_none()

    @classmethod
    def insert_or_update(cls, data: dict):
        # 检查是否已存在相同 back_test_result_key 和 transaction_time 的记录
        # existing = session.query(cls).filter(
        #     cls.back_test_result_key == data['back_test_result_key'],
        #     cls.transaction_time == data['transaction_time']
        # ).first()
        #
        # if existing:
        #     # 更新现有记录
        #     for key, value in data.items():
        #         setattr(existing, key, value)
        #     result = existing
        # else:
        # 插入新记录
        result = cls(**data)
        session.add(result)

        session.commit()
        return result

    @classmethod
    def delete_by_id(cls, id: int):
        stmt = delete(cls).where(cls.id == id)
        session.execute(stmt)
        session.commit()

    @classmethod
    def delete_all(cls):
        stmt = delete(cls)
        session.execute(stmt)
        session.commit()


if __name__ == '__main__':
    BacktestRecord.delete_all()
