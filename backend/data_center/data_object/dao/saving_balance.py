from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from backend.decorator.decorator import add_docstring

Base = declarative_base()


@add_docstring("余币宝余额")
class SavingBalance(Base):

    __tablename__ ='saving_balance'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    amt = Column(String, comment='币种金额')
    ccy = Column(String, comment='币种')
    earnings = Column(String, comment='币种持仓收益')
    loan_amt = Column(String, comment='已出借数量')
    pending_amt = Column(String, comment='未出借数量')
    rate = Column(String, comment='币种持仓收益')
    redempt_amt = Column(String, comment='可赎回数量-已废弃')
