from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, Float
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
    
    # 调度相关字段
    status = Column(String(20), nullable=False, default='stopped')  # running, stopped, paused
    schedule_frequency = Column(String(20), nullable=False)  # 1h, 4h, 1d, etc.
    next_execution_time = Column(DateTime)
    last_execution_time = Column(DateTime)
    
    # 交易相关字段
    symbols = Column(JSON, nullable=False)  # 交易对列表
    entry_per_trans = Column(Float, nullable=True)  # 每笔入场资金
    loss_per_trans = Column(Float, nullable=True)  # 每笔最大损失
    commission = Column(Float, default=0.001)
    
    # 统计字段
    total_executions = Column(Integer, default=0)
    total_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def list_all(cls, status=None):
        """获取所有策略实例"""
        session = Session()
        try:
            query = session.query(cls)
            if status:
                query = query.filter(cls.status == status)
            instances = query.all()
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
            'status': self.status,
            'schedule_frequency': self.schedule_frequency,
            'next_execution_time': self.next_execution_time.strftime('%Y-%m-%d %H:%M:%S') if self.next_execution_time else None,
            'last_execution_time': self.last_execution_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_execution_time else None,
            'symbols': self.symbols,
            'entry_per_trans': self.entry_per_trans,
            'loss_per_trans': self.loss_per_trans,
            'commission': self.commission,
            'total_executions': self.total_executions,
            'total_trades': self.total_trades,
            'total_profit': self.total_profit,
            'win_rate': self.win_rate,
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
    def create(cls, strategy_id, strategy_name, strategy_type, strategy_params,
              schedule_frequency, symbols, entry_per_trans=None, 
              loss_per_trans=None, commission=0.001):
        """创建策略实例"""
        session = Session()
        try:
            # 验证互斥逻辑
            if entry_per_trans is None and loss_per_trans is None:
                raise ValueError("必须指定entry_per_trans或loss_per_trans其中一个")
            if entry_per_trans is not None and loss_per_trans is not None:
                raise ValueError("entry_per_trans和loss_per_trans只能指定其中一个")
                
            instance = cls(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                strategy_type=strategy_type,
                strategy_params=strategy_params,
                schedule_frequency=schedule_frequency,
                symbols=symbols,
                entry_per_trans=entry_per_trans,
                loss_per_trans=loss_per_trans,
                commission=commission
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

    def update(self, **kwargs):
        """更新策略实例"""
        session = Session()
        try:
            instance = session.query(self.__class__).filter(self.__class__.id == self.id).first()
            if instance:
                for key, value in kwargs.items():
                    if hasattr(instance, key) and value is not None:
                        setattr(instance, key, value)
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
    def update_status(cls, instance_id, status):
        """更新策略实例状态"""
        session = Session()
        try:
            instance = session.query(cls).filter(cls.id == instance_id).first()
            if instance:
                instance.status = status
                instance.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新策略实例状态失败: {str(e)}")
            return False
        finally:
            session.close()

    @classmethod
    def update_execution_time(cls, instance_id, last_execution_time, next_execution_time=None):
        """更新执行时间"""
        session = Session()
        try:
            instance = session.query(cls).filter(cls.id == instance_id).first()
            if instance:
                instance.last_execution_time = last_execution_time
                if next_execution_time:
                    instance.next_execution_time = next_execution_time
                instance.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新执行时间失败: {str(e)}")
            return False
        finally:
            session.close()

    @classmethod
    def update_statistics(cls, instance_id, total_executions=None, total_trades=None,
                         total_profit=None, win_rate=None):
        """更新统计信息"""
        session = Session()
        try:
            instance = session.query(cls).filter(cls.id == instance_id).first()
            if instance:
                if total_executions is not None:
                    instance.total_executions = total_executions
                if total_trades is not None:
                    instance.total_trades = total_trades
                if total_profit is not None:
                    instance.total_profit = total_profit
                if win_rate is not None:
                    instance.win_rate = win_rate
                instance.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新统计信息失败: {str(e)}")
            return False
        finally:
            session.close()

    @classmethod
    def update_execution_stats(cls, instance_id):
        """更新执行统计信息（基于执行记录）"""
        session = Session()
        try:
            # 导入在这里以避免循环导入
            from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord
            
            instance = session.query(cls).filter(cls.id == instance_id).first()
            if instance:
                # 获取所有成功的执行记录
                records = StrategyExecutionRecord.get_by_instance_id(instance_id, limit=1000)
                completed_records = [r for r in records if r.get('status') == 'completed']
                
                if completed_records:
                    # 计算统计信息
                    total_executions = len(completed_records)
                    total_trades = sum(r.get('total_trades', 0) for r in completed_records)
                    total_profit = sum(r.get('total_profit', 0) for r in completed_records)
                    
                    # 计算胜率
                    total_successful = sum(r.get('successful_trades', 0) for r in completed_records)
                    win_rate = (total_successful / total_trades * 100) if total_trades > 0 else 0
                    
                    # 更新实例统计信息
                    instance.total_executions = total_executions
                    instance.total_trades = total_trades
                    instance.total_profit = total_profit
                    instance.win_rate = win_rate
                    instance.updated_at = datetime.now()
                    session.commit()
                    return True
                    
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新执行统计信息失败: {str(e)}")
            return False
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

# 创建表
Base.metadata.create_all(engine) 