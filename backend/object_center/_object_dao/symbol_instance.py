# 创建基类
from typing import List

from sqlalchemy import Column, String, Integer, select
from sqlalchemy.orm import declarative_base

from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


# 定义 ORM 模型类
class SymbolInstance(Base):
    __tablename__ = 'symbol_instance'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='交易对实例ID')
    symbol = Column(String(255), nullable=False, comment='交易对')

    # interval = Column(String(255), nullable=False, comment='时间窗口')

    @classmethod
    def query_all(cls):
        results = session.scalars(
            select(cls)
        ).all()
        return {'symbol_list': [str(result.symbol) for result in results]} if results else {
            'symbol_list': []}

    @classmethod
    def query_all_usdt(cls) -> list:
        results = session.scalars(
            select(cls)
        ).all()
        return [f"{result.symbol}-USDT" for result in results]


def query_symbol_instance(symbol) -> SymbolInstance:
    return session.query(SymbolInstance).filter_by(symbol=symbol).first()


def add_symbol_instance(symbol):
    # 检查是否已存在相同的记录
    existing_instance = session.query(SymbolInstance).filter_by(symbol=symbol).first()
    if existing_instance:
        print(f"Symbol: {symbol} already exists.")
        return
    new_symbol_instance = SymbolInstance(symbol=symbol)
    session.add(new_symbol_instance)
    session.commit()


def query_all_symbol_instance() -> List[SymbolInstance]:
    return DatabaseUtils.get_db_session().query(SymbolInstance).all()


if __name__ == '__main__':
    # # 添加一个新的交易对实例
    add_symbol_instance('BTC')
    # # 查询交易对实例
    # result = query_symbol_instance('BTC', '4H')
    # print(result.symbol, result.interval)

    # resList: List[SymbolInstance] = query_all_symbol_instance()
    # for result in resList:
    #     print(result.symbol)
    # print(f"total count:{len(resList)}")

    result = SymbolInstance.query_all()
    print(result)
