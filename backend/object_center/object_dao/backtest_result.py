from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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

