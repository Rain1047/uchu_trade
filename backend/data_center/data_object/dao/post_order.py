from sqlalchemy import Column, String, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from backend.service.utils import *

Base = declarative_base()


class PostOrderDB(Base):
    __tablename__ = 'post_order_history'

    # 字段定义
    algo_cl_ord_id = Column(String, comment='客户自定义策略订单ID')
    algo_id = Column(String, comment='策略委托单ID')
    ord_id = Column(String, comment='订单ID')
    cl_ord_id = Column(String, comment='客户端订单ID')
    s_code = Column(String, comment='事件执行结果的code，0代表成功')
    s_msg = Column(String, comment='事件执行失败时的msg')
    tag = Column(String, comment='订单标签')
    inst_id = Column(String, comment='交易对')
    side = Column(String, comment='交易方向')
    c_time = Column(String, comment='创建时间')
    u_time = Column(String, comment='更新时间')
    status = Column(String, comment='订单状态')
    operation_mode = Column(String, comment='操作模式')

    # 根据 SQLAlchemy 的规范，你可能还需要主键字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')


if __name__ == '__main__':
    try:
        # Get the database engine
        engine = DatabaseUtils.get_engine()

        # Create the table in the database
        Base.metadata.create_all(engine)
        print("Table created successfully.")

    except SQLAlchemyError as e:
        print(f"Error occurred: {e}")
