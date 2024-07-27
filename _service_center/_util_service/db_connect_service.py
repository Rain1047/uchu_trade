import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from _data_center.data_object.dao.st_instance_dao import StInstance
from _utils.utils import *

def get_project_root():
    # 获取当前脚本所在文件夹的绝对路径
    current_dir = Path(__file__).resolve().parent
    # 返回项目根目录的绝对路径
    return current_dir.parents[1]


def get_db_session():
    # 获取项目根目录的绝对路径
    project_root = get_project_root()
    # 构建数据库文件的绝对路径
    db_absolute_path = project_root / '_data_center' / 'trade_db.db'
    # 创建数据库连接引擎
    engine = create_engine(f'sqlite:///{db_absolute_path}')
    print(f'sqlite:///{db_absolute_path}')
    # 创建会话类
    Session = sessionmaker(bind=engine)
    # 创建会话实例并返回
    return Session()


if __name__ == '__main__':
    tf = "4H"
    session = DatabaseUtils.get_db_session()
    st_instance_list = session.query(StInstance) \
        .filter(StInstance.switch == 0, StInstance.is_del == 0, StInstance.time_frame == tf) \
        .all()
    # print the result
    for st_instance in st_instance_list:
        print(st_instance.id, st_instance.trade_pair)
    print(get_project_root())
