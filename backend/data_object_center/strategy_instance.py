from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime
import logging
from backend.data_object_center.base import Base, engine, Session

# 配置日志
logger = logging.getLogger(__name__)

class StrategyInstance(Base):
    __tablename__ = 'strategy_instance'

    id = Column(Integer, primary_key=True)
    strategy_id = Column(String(50), nullable=False)
    strategy_name = Column(String(50), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    strategy_params = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def list_all(cls):
        """获取所有策略实例"""
        session = Session()
        try:
            instances = session.query(cls).all()
            return [instance.to_dict() for instance in instances]
        except Exception as e:
            logger.error(f"获取策略实例列表失败: {str(e)}")
            return []
        finally:
            session.close()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'strategy_name': self.strategy_name,
            'strategy_type': self.strategy_type,
            'strategy_params': self.strategy_params,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def get_by_id(cls, instance_id):
        """根据ID获取策略实例"""
        session = Session()
        try:
            instance = session.query(cls).filter(cls.id == instance_id).first()
            return instance.to_dict() if instance else None
        except Exception as e:
            logger.error(f"获取策略实例失败: {str(e)}")
            return None
        finally:
            session.close()

    @classmethod
    def create(cls, strategy_id, strategy_name, strategy_type, strategy_params):
        """创建策略实例"""
        session = Session()
        try:
            instance = cls(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                strategy_type=strategy_type,
                strategy_params=strategy_params
            )
            session.add(instance)
            session.commit()
            return instance.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"创建策略实例失败: {str(e)}")
            return None
        finally:
            session.close()

    def update(self, strategy_name=None, strategy_params=None):
        """更新策略实例"""
        session = Session()
        try:
            instance = session.query(self.__class__).filter(self.__class__.id == self.id).first()
            if instance:
                if strategy_name is not None:
                    instance.strategy_name = strategy_name
                if strategy_params is not None:
                    instance.strategy_params = strategy_params
                instance.updated_at = datetime.now()
                session.commit()
                return instance.to_dict()
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"更新策略实例失败: {str(e)}")
            return None
        finally:
            session.close()

    @classmethod
    def delete(cls, instance_id):
        """删除策略实例"""
        session = Session()
        try:
            instance = session.query(cls).filter(cls.id == instance_id).first()
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除策略实例失败: {str(e)}")
            return False
        finally:
            session.close() 