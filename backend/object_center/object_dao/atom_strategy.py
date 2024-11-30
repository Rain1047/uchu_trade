from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AtomStrategy(Base):
    __tablename__ = 'atom_strategy'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String, comment='策略名称')
    code = Column(String, comment='策略Code')
    type = Column(String, comment='策略类型 入场/出场/过滤')
    side = Column(String, comment='进场方向')
