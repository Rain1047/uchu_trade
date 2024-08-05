import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend._data_center.data_object.dao.od_instance_dao import OrderInstance



# 创建数据库连接引擎
engine = create_engine('mysql+mysqlconnector://root:rain1104@localhost/trade_db')
# 创建会话类
Session = sessionmaker(bind=engine)
# 创建会话实例
session = Session()

def timestamp_to_datetime_milliseconds(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000.0
    return datetime.datetime.fromtimestamp(timestamp_sec)


if __name__ == '__main__':
    order_instance = OrderInstance(
        order_id="1",
        st_ins_code="1",
        entry_time="1",
        side="long",
        order_info="order info test",
        gmt_create=timestamp_to_datetime_milliseconds(1712335064648),
        gmt_modified=datetime.datetime.now(),
    )
    # 将 OrderInstance 对象添加到会话中
    session.add(order_instance)
    # 提交会话以将更改保存到数据库中
    session.commit()
    # 关闭会话
    session.close()
