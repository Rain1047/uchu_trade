from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
import logging
from backend.data_object_center.base import Base, engine, Session

logger = logging.getLogger(__name__)

class StrategyExecutionRecord(Base):
    """策略执行记录"""
    __tablename__ = 'strategy_execution_records'
    
    id = Column(Integer, primary_key=True)
    instance_id = Column(Integer, ForeignKey('strategy_instance.id'), nullable=False)
    
    # 执行信息
    execution_time = Column(DateTime, nullable=False, default=datetime.now)
    status = Column(String(20), nullable=False)  # running, completed, failed, cancelled
    error_message = Column(String(500))
    
    # 交易信息
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    
    # 收益信息
    total_profit = Column(Float, default=0.0)
    profit_rate = Column(Float, default=0.0)
    
    # 详细信息
    trade_details = Column(JSON)  # 存储具体的交易记录
    metrics = Column(JSON)  # 存储其他指标
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    @classmethod
    def create(cls, instance_id, status='running'):
        """创建执行记录"""
        session = Session()
        try:
            record = cls(
                instance_id=instance_id,
                status=status,
                execution_time=datetime.now()
            )
            session.add(record)
            session.commit()
            return record.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"创建执行记录失败: {str(e)}")
            return None
        finally:
            session.close()
    
    @classmethod
    def update_status(cls, record_id, status, error_message=None):
        """更新执行状态"""
        session = Session()
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            if record:
                record.status = status
                record.error_message = error_message
                record.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新执行状态失败: {str(e)}")
            return False
        finally:
            session.close()
    
    @classmethod
    def update_trade_info(cls, record_id, total_trades=None, successful_trades=None, 
                         failed_trades=None, total_profit=None, profit_rate=None, 
                         trade_details=None, metrics=None):
        """更新交易信息"""
        session = Session()
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            if record:
                if total_trades is not None:
                    record.total_trades = total_trades
                if successful_trades is not None:
                    record.successful_trades = successful_trades
                if failed_trades is not None:
                    record.failed_trades = failed_trades
                if total_profit is not None:
                    record.total_profit = total_profit
                if profit_rate is not None:
                    record.profit_rate = profit_rate
                if trade_details is not None:
                    record.trade_details = trade_details
                if metrics is not None:
                    record.metrics = metrics
                record.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新交易信息失败: {str(e)}")
            return False
        finally:
            session.close()
    
    @classmethod
    def get_by_instance_id(cls, instance_id, limit=100):
        """根据实例ID获取执行记录列表"""
        session = Session()
        try:
            records = session.query(cls).filter(
                cls.instance_id == instance_id
            ).order_by(cls.execution_time.desc()).limit(limit).all()
            return [record.to_dict() for record in records]
        except Exception as e:
            logger.error(f"获取执行记录失败: {str(e)}")
            return []
        finally:
            session.close()
    
    @classmethod
    def get_by_id(cls, record_id):
        """根据ID获取单条执行记录"""
        session = Session()
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            return record.to_dict() if record else None
        except Exception as e:
            logger.error(f"获取执行记录失败: {str(e)}")
            return None
        finally:
            session.close()
    
    @classmethod
    def get_latest_by_instance_id(cls, instance_id):
        """获取策略实例的最新执行记录"""
        session = Session()
        try:
            record = session.query(cls).filter(
                cls.instance_id == instance_id
            ).order_by(cls.execution_time.desc()).first()
            return record.to_dict() if record else None
        except Exception as e:
            logger.error(f"获取最新执行记录失败: {str(e)}")
            return None
        finally:
            session.close()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'instance_id': self.instance_id,
            'execution_time': self.execution_time.strftime('%Y-%m-%d %H:%M:%S') if self.execution_time else None,
            'status': self.status,
            'error_message': self.error_message,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'total_profit': self.total_profit,
            'profit_rate': self.profit_rate,
            'trade_details': self.trade_details,
            'metrics': self.metrics,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


# 创建表
Base.metadata.create_all(engine) 