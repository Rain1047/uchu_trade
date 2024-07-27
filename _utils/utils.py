import this
from datetime import datetime, timedelta
import os
import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DateUtils:
    @staticmethod
    def current_time2string():
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    @staticmethod
    def past_time2string(days):
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def get_config():
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_file_path = os.path.join(script_dir, '../config.json')
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return config


class CheckUtils:
    @staticmethod
    def is_empty(value):
        if value is None:
            return True
        if isinstance(value, (str, list, tuple, dict, set)):
            return len(value) == 0
        return False

    @staticmethod
    def is_not_empty(value):
        return not CheckUtils.is_empty(value)


class DatabaseUtils:
    @staticmethod
    def get_db_session():
        # 获取项目根目录的绝对路径
        project_root = DatabaseUtils.get_project_root()
        # 构建数据库文件的绝对路径
        db_absolute_path = project_root / '_data_center' / 'trade_db.db'
        # 创建数据库连接引擎
        engine = create_engine(f'sqlite:///{db_absolute_path}')
        print(f'sqlite:///{db_absolute_path}')
        # 创建会话类
        Session = sessionmaker(bind=engine)
        # 创建会话实例并返回
        return Session()

    @staticmethod
    def get_project_root():
        # 获取当前脚本所在文件夹的绝对路径
        current_dir = Path(__file__).resolve().parent
        print(current_dir)
        # 返回项目根目录的绝对路径
        return current_dir.parents[0]


# 示例用法
if __name__ == "__main__":
    # print(DateUtils.current_time2string())
    #
    # print(DateUtils.past_time2string(20))

    print(DatabaseUtils.get_project_root())
