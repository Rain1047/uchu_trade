from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select, delete

from backend.utils.utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class BacktestResult(Base):
    __tablename__ = 'backtest_result'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    back_test_result_key = Column(Integer, comment='回测结果FK')
    symbol = Column(String, comment='交易对')
    strategy_id = Column(String, comment='策略实例id')
    strategy_name = Column(String, comment='策略实例名称')
    test_finished_time = Column(String, comment='运行时间')
    buy_signal_count = Column(Integer, comment='买入信号次数')
    sell_signal_count = Column(Integer, comment='卖出信号次数')
    transaction_count = Column(Integer, comment='交易次数')
    profit_count = Column(Integer, comment='获利次数')
    loss_count = Column(Integer, comment='损失次数')
    profit_total_count = Column(Integer, comment='总收益')
    profit_average = Column(Integer, comment='平均收益')
    profit_rate = Column(Integer, comment='收益率')
    gmt_create = Column(String, nullable=False, comment='生成时间')
    gmt_modified = Column(String, nullable=False, comment='更新时间')

    @classmethod
    def list_all(cls):
        stmt = select(cls)
        return session.execute(stmt).scalars().all()

    @classmethod
    def get_by_id(cls, id: int):
        stmt = select(cls).where(cls.id == id)
        return session.execute(stmt).scalar_one_or_none()

    @classmethod
    def insert_or_update(cls, data: dict):
        # 检查是否已存在相同 strategy_id 的记录
        existing = session.query(cls).filter(
            cls.back_test_result_key == data['back_test_result_key']
        ).first()

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if existing:
            # 更新现有记录
            data['gmt_modified'] = current_time
            for key, value in data.items():
                setattr(existing, key, value)
            result = existing
        else:
            # 插入新记录
            data['gmt_create'] = current_time
            data['gmt_modified'] = current_time
            result = cls(**data)
            session.add(result)

        session.commit()
        return result

    @classmethod
    def delete_by_id(cls, id: int):
        stmt = delete(cls).where(cls.id == id)
        session.execute(stmt)
        session.commit()


if __name__ == '__main__':
    result = BacktestResult.list_all()
    print(result)
