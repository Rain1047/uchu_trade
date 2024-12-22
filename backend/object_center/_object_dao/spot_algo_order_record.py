from typing import Dict, List, Optional, Any

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class SpotTradeConfig(Base):
    __tablename__ = 'spot_algo_order_record'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ccy = Column(String, comment='币种')
    type = Column(String, comment='类型')
    config_id = Column(String, comment='配置id')
    sz = Column(String, comment='仓位')
    amount = Column(String, comment='金额/USDT')
    target_price = Column(String, comment='目标价格')
    algoId = Column(String, comment='止损订单id')
    ordId = Column(String, comment='限价订单id')
    status = Column(String, comment='订单状态')
    create_time = Column(Date, comment='创建时间')

