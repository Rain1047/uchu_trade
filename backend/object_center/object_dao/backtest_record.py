from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BacktestRecord(Base):
    __tablename__ = 'backtest_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    back_test_result_key = Column(Integer, comment='回测结果FK')

    transaction_time = Column(String, comment='交易时间')
    transaction_result = Column(String, comment='交易结果')
