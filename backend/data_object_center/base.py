from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 获取数据库URL
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./trading.db')

# 创建数据库引擎
engine = create_engine(DB_URL, echo=True)

# 创建基类
Base = declarative_base()

# 创建会话工厂
Session = sessionmaker(bind=engine) 