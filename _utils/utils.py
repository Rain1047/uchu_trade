# import this
import logging
from datetime import datetime, timedelta
import os
import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd


class DateUtils:
    @staticmethod
    def current_time2string():
        now = datetime.now()
        print(now)
        return now.strftime("%Y-%m-%d")

    @staticmethod
    def past_time2string(days):
        date = datetime.now() - timedelta(days=days)
        print("past_time: " + str(date))
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


class FormatUtils:

    @staticmethod
    def format_json(data):
        try:
            # 尝试解析数据，如果数据格式不正确，这里会抛出异常
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return None

    @staticmethod
    def dict2df(data_dict):
        # Define column names
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
        # Create DataFrame
        df = pd.DataFrame(data_dict['data'], columns=columns)[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        # Convert other columns to numeric
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
        # Revert the frame
        df = df.iloc[::-1]
        return df

    @staticmethod
    def dict2dao(model_class, data_dict):
        # 创建模型实例
        instance = model_class()

        for key, value in data_dict.items():
            # 将 camelCase 键转换为 snake_case
            snake_case_key = FormatUtils.to_snake_case(key)

            # 处理嵌套的字典，比如 linkedAlgoOrd
            if isinstance(value, dict):
                # 将嵌套字典展开到父字典中
                for nested_key, nested_value in value.items():
                    nested_snake_key = f"{snake_case_key}_{FormatUtils.to_snake_case(nested_key)}"
                    setattr(instance, nested_snake_key, FormatUtils.convert_value(nested_value))
            else:
                # 设置实例的属性
                if hasattr(instance, snake_case_key):
                    setattr(instance, snake_case_key, FormatUtils.convert_value(value))
                else:
                    print(f"警告: {snake_case_key} 不是 {model_class.__name__} 的属性")

        return instance

    @staticmethod
    def to_snake_case(camel_case_str):
        # 将 camelCase 转换为 snake_case
        return ''.join(['_' + i.lower() if i.isupper() else i for i in camel_case_str]).lstrip('_')

    @staticmethod
    def convert_value(value):
        # 将非字符串类型转换为字符串
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, dict)):
            return json.dumps(value)
        return value


# 示例用法
if __name__ == "__main__":
    # print(DateUtils.current_time2string())
    #
    # print(DateUtils.past_time2string(20))

    # print(DatabaseUtils.get_project_root())

    print(ConfigUtils.get_config())
