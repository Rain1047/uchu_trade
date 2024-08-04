# import this
import logging
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


class ConfigUtils:
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
    _instance = None
    _session = None
    _engine = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseUtils, cls).__new__(cls)
            cls._setup()
        return cls._instance

    @classmethod
    def _setup(cls):
        # 获取项目根目录的绝对路径
        project_root = cls.get_project_root()
        # 构建数据库文件的绝对路径
        db_absolute_path = project_root / '_data_center' / 'trade_db.db'
        # 创建数据库连接引擎
        cls._engine = create_engine(f'sqlite:///{db_absolute_path}')
        # 创建会话类
        cls._Session = sessionmaker(bind=cls._engine)
        logging.info("Database setup complete.")

    @staticmethod
    def get_db_session():
        if DatabaseUtils._session is None:
            # Ensure that _setup() has been called and _Session has been initialized
            if DatabaseUtils._engine is None or DatabaseUtils._Session is None:
                DatabaseUtils._setup()
            DatabaseUtils._session = DatabaseUtils._Session()
        return DatabaseUtils._session

    @staticmethod
    def get_project_root():
        # 获取当前脚本所在文件夹的绝对路径
        current_dir = Path(__file__).resolve().parent
        print(current_dir)
        # 返回项目根目录的绝对路径
        return current_dir.parents[0]

    @staticmethod
    def save(data_object):
        session = DatabaseUtils.get_db_session()
        try:
            session.add(data_object)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"保存数据时出错: {e}")
            raise
        finally:
            # 这里不再关闭 session，因为我们使用单例模式管理它
            pass


class JSONUtils:

    @staticmethod
    def format_json(data):
        try:
            # 尝试解析数据，如果数据格式不正确，这里会抛出异常
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return None


# 示例用法
if __name__ == "__main__":
    # print(DateUtils.current_time2string())
    #
    # print(DateUtils.past_time2string(20))

    # print(DatabaseUtils.get_project_root())

    print(ConfigUtils.get_config())
