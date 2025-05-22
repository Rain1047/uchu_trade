# import this
import logging
from datetime import timedelta, timezone
import json
import os
from pathlib import Path
from typing import Optional
import yfinance as yf

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
import uuid
import time
import random


class LogConfig:
    """统一的日志配置类"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogConfig, cls).__new__(cls)
        return cls._instance

    @classmethod
    def setup(cls, level: int = logging.INFO):
        """设置日志配置"""
        if cls._initialized:
            return

        # 创建日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 添加文件处理器
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'app.log')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        cls._initialized = True

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        return logging.getLogger(name)


class SymbolFormatUtils:

    @staticmethod
    def get_base_symbol(instId: str) -> str:
        return instId.split("-")[0]

    @staticmethod
    def get_usdt(instId: str) -> str:
        return instId.split("-")[0] + "-USDT"

    @staticmethod
    def get_swap_usdt(instId: str):
        return instId.split("-")[0] + "-USDT-SWAP"


class DateUtils:
    @staticmethod
    def current_time2string():
        now = datetime.now()
        logger = LogConfig.get_logger(__name__)
        logger.debug(f"当前时间: {now}")
        return now.strftime("%Y-%m-%d")

    @staticmethod
    def past_time2string(days):
        date = datetime.now() - timedelta(days=days)
        logger = LogConfig.get_logger(__name__)
        logger.debug(f"过去时间: {date}")
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def milliseconds() -> int:
        # 获取当前时间
        now = datetime.now()
        # 获取当前时间的时间戳（秒）
        timestamp_seconds = now.timestamp()
        # 获取毫秒部分
        milliseconds = now.microsecond // 1000
        # 转换为毫秒级别时间戳
        return int(timestamp_seconds * 1000) + milliseconds

    @staticmethod
    def get_current_timestamp() -> str:
        # 获取当前时间，并转为 UTC 时区
        now = datetime.now(timezone.utc)
        # 格式化为 ISO 8601 格式，包含毫秒
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


class ConfigUtils:
    @staticmethod
    def get_config() -> json:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Navigate to the correct config file path
        config_file_path = os.path.join(script_dir, '../config.json')

        # Check if the config file exists
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Config file not found at {config_file_path}")

        # Load and return the config
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

    @staticmethod
    def get_engine():
        project_root = DatabaseUtils.get_project_root()
        db_absolute_path = project_root / 'backend' / 'data_center' / 'trade_db.db'
        return create_engine(f'sqlite:///{db_absolute_path}')

    @classmethod
    def _setup(cls):
        try:
            # 获取项目根目录的绝对路径
            project_root = cls.get_project_root()
            # 构建数据库文件的绝对路径
            db_absolute_path = project_root / 'backend' / 'data_center' / 'trade_db.db'
            logger = LogConfig.get_logger(__name__)
            logger.info(f"数据库路径: {db_absolute_path}")
            # 创建数据库连接引擎
            cls._engine = create_engine(f'sqlite:///{db_absolute_path}')
            # 创建会话类
            cls._Session = sessionmaker(bind=cls._engine)
            logger.info("数据库设置完成")
        except Exception as e:
            logger = LogConfig.get_logger(__name__)
            logger.error(f"数据库设置出错: {e}")
            pass

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
        logger = LogConfig.get_logger(__name__)
        logger.info(f"当前目录: {current_dir}")
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


class UuidUtils:
    @staticmethod
    def generate_32_digit_numeric_id():
        # 生成 UUID 并取其十六进制表示的部分
        uuid_hex = uuid.uuid4().hex

        # 获取当前时间戳（秒）并取其数字部分
        timestamp = int(time.time())

        # 生成一个随机数
        random_number = random.randint(1000, 9999)  # 生成一个随机数

        # 组合 UUID 的十六进制部分、时间戳和随机数
        combined_string = f"{uuid_hex}{timestamp}{random_number}"

        # 取前32位纯数字
        pure_numeric_id = ''.join(filter(str.isdigit, combined_string))[:32]

        return pure_numeric_id


class FormatUtils:

    @staticmethod
    def format_json(data):
        try:
            # 尝试解析数据，如果数据格式不正确，这里会抛出异常
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger = LogConfig.get_logger(__name__)
            logger.error(f"JSON 解析错误: {e}")
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
                    logger = LogConfig.get_logger(__name__)
                    logger.warning(f"警告: {snake_case_key} 不是 {model_class.__name__} 的属性")

        return instance

    @staticmethod
    def dao2dict(obj, *fields: Optional[str]) -> dict:
        """
        将对象的指定字段转换为字典，去除所有的 _sa_instance_state 属性。

        :param obj: 需要转换为字典的对象
        :param fields: 需要包含在字典中的字段名
        :return: 字典格式的数据
        """
        if not fields:
            # 如果没有指定字段，尝试调用对象的 to_dict 方法
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()  # Call the to_dict method if it exists
            else:
                # Fallback to vars and filter out _sa_instance_state
                return {k: v for k, v in vars(obj).items() if k != '_sa_instance_state'}

        # 返回指定字段的字典，去除 _sa_instance_state
        return {field: getattr(obj, field, None) for field in fields if field != '_sa_instance_state'}

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
    print(DatabaseUtils.get_db_session())
