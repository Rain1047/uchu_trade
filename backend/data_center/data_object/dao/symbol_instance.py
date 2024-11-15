# 创建基类
from typing import List

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base
from tvDatafeed import Interval

from backend.utils.utils import DatabaseUtils

Base = declarative_base()


# 定义 ORM 模型类
class SymbolInstance(Base):
    __tablename__ = 'symbol_instance'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='交易对实例ID')
    symbol = Column(String(255), nullable=False, comment='交易对')
    interval = Column(String(255), nullable=False, comment='时间窗口')


def query_symbol_instance(symbol, interval) -> SymbolInstance:
    session = DatabaseUtils.get_db_session()
    return session.query(SymbolInstance).filter_by(symbol=symbol, interval=interval).first()


def add_symbol_instance(symbol, interval):
    session = DatabaseUtils.get_db_session()
    # 检查是否已存在相同的记录
    existing_instance = session.query(SymbolInstance).filter_by(symbol=symbol, interval=interval).first()
    if existing_instance:
        print(f"Symbol: {symbol} Interval: {interval} already exists.")
        return
    new_symbol_instance = SymbolInstance(symbol=symbol, interval=interval)
    session.add(new_symbol_instance)
    session.commit()


def query_all_symbol_instance() -> List[SymbolInstance]:
    return DatabaseUtils.get_db_session().query(SymbolInstance).all()


if __name__ == '__main__':
    # # 添加一个新的交易对实例
    add_symbol_instance('BTC', Interval.in_15_minute.value)
    add_symbol_instance('BTC', Interval.in_5_minute.value)
    add_symbol_instance('BTC', Interval.in_1_hour.value)
    add_symbol_instance('BTC', Interval.in_2_hour.value)

    # # 查询交易对实例
    # result = query_symbol_instance('BTC', '4H')
    # print(result.symbol, result.interval)

    resList: List[SymbolInstance] = query_all_symbol_instance()
    for res in resList:
        print(res.symbol, res.interval)
    print(f"total count:{len(resList)}")
