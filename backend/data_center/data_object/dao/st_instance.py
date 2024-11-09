from typing import List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.service.utils import DatabaseUtils

# 创建基类
Base = declarative_base()


# 定义 ORM 模型类
class StInstance(Base):
    __tablename__ = 'st_instance'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='策略实例ID')
    name = Column(String(255), nullable=False, comment='策略实例名称')
    trade_pair = Column(String(255), nullable=False, comment='交易对')
    side = Column(String(255), nullable=True, comment="交易方向")
    entry_per_trans = Column(Float, nullable=False, comment='每笔入场金额')
    loss_per_trans = Column(Float, nullable=False, comment='每笔损失金额')
    time_frame = Column(String(255), nullable=False, comment='时间窗口大小')
    entry_st_code = Column(String(255), nullable=False, comment='入场策略code')
    exit_st_code = Column(String(255), nullable=False, comment='退出策略code')
    filter_st_code = Column(String(255), nullable=False, comment='过滤策略code')
    # exit_by_time = Column(Integer, comment='根据时间退出')  # delete
    stop_loss_config = Column(String, comment='止损配置')
    schedule_config = Column(String, comment='调度配置')
    switch = Column(Integer, comment='开关')
    is_del = Column(Integer, nullable=False, default=0, comment='0: 生效 1:已删除')
    env = Column(String, comment='运行环境')
    gmt_create = Column(String, nullable=False, comment='生成时间')
    gmt_modified = Column(String, nullable=False, comment='更新时间')


def query_all_st_instance() -> List[StInstance]:
    return DatabaseUtils.get_db_session().query(StInstance).all()


if __name__ == '__main__':
    session = DatabaseUtils.get_db_session()

    # 查询所有策略实例

    # # 创建一条记录
    # new_instance = StInstance(
    #     name='比特币双布林带策略',
    #     trade_pair='BTC-USDT',
    #     position=1000,
    #     time_frame="4H",
    #     entry_st_code='entry_code',
    #     exit_st_code='exit_code',
    #     gmt_create=datetime.now(),
    #     gmt_modified=datetime.now()
    # )
    #
    # # 将记录添加到会话并提交
    # # 查询所有订单实例
    # st_instance_list = session.query(StInstance).all()
    # for st_instance in st_instance_list:
    #     print(st_instance.id, st_instance.trade_pair)
    #
    # # 关闭会话
    # session.close()
