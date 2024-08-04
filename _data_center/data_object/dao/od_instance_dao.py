from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 创建基类
Base = declarative_base()


class OrderInstance(Base):
    __tablename__ = 'order_instance'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    order_id = Column(Integer, nullable=False, comment='订单实例ID')
    st_ins_code = Column(String(255), nullable=False, comment='策略实例id')
    entry_time = Column(String(255), nullable=True, comment='根据哪一个时间入场的')
    side = Column(String(20), nullable=False, comment='方向 Long做多 Short做空')
    order_info = Column(Text, nullable=False, comment='订单信息')
    gmt_create = Column(DateTime, nullable=False, comment='生成时间')
    gmt_modified = Column(DateTime, nullable=False, comment='修改时间')
    # 定义索引
    idx_order_id = Index('idx_order_id', order_id)
