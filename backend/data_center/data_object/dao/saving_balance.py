from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from backend.service.decorator import add_docstring

Base = declarative_base()


@add_docstring("余币宝余额")
class CryptoData(Base):

    amt = Column(String, comment='币种金额')
    ccy = Column(String, comment='币种')
    earnings = Column(String, comment='币种持仓收益')
    loanAmt = Column(String, comment='已出借数量')
    pendingAmt = Column(String, comment='未出借数量')
    rate = Column(String, comment='币种持仓收益')
