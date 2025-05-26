from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

# 复用项目公共 Base
from backend.data_object_center.base import Base


class SystemPrompt(Base):
    """System Prompt ORM 表

    用于存储可复用的对话 System Prompt。支持富文本 Markdown。"""

    __tablename__ = "system_prompt"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False, comment="Prompt 名称")
    content = Column(Text, nullable=False, comment="Markdown / 富文本内容")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 