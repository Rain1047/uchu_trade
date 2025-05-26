from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from backend.data_object_center.base import Base


class StrategyJob(Base):
    """长链路任务状态表"""

    __tablename__ = "strategy_job"

    id = Column(String(12), primary_key=True)  # uuid4 hex[:12]
    file_id = Column(Integer, nullable=False)
    prompt_id = Column(Integer, nullable=False)
    progress = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending / running / success / error
    output_py = Column(String(255), nullable=True)
    message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True) 