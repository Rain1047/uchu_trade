from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from backend.data_object_center.base import Base


class UploadFile(Base):
    """用户上传的文件元数据"""

    __tablename__ = "upload_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    stored_path = Column(String(255), nullable=False)
    file_type = Column(String(12), nullable=False)
    size = Column(Integer, nullable=False)
    status = Column(String(20), default="saved")  # saved / processed / failed
    created_at = Column(DateTime, default=datetime.utcnow) 