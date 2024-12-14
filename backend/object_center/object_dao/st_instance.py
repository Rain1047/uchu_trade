from typing import List

from sqlalchemy import Column, Integer, String, select, update
from sqlalchemy.ext.declarative import declarative_base

from backend.utils import DatabaseUtils

# 创建基类
Base = declarative_base()
session = DatabaseUtils.get_db_session()


# 定义 ORM 模型类
class StrategyInstance(Base):
    __tablename__ = 'st_instance'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='策略实例ID')
    name = Column(String(255), nullable=False, comment='策略实例名称')
    trade_pair = Column(String(255), nullable=False, comment='交易对')
    side = Column(String(255), nullable=True, comment="交易方向")
    entry_per_trans = Column(Integer, nullable=False, comment='每笔入场金额')
    loss_per_trans = Column(Integer, nullable=False, comment='每笔损失金额')
    time_frame = Column(String(255), nullable=False, comment='时间窗口大小')
    entry_st_code = Column(String(255), nullable=False, comment='入场策略code')
    exit_st_code = Column(String(255), nullable=False, comment='退出策略code')
    filter_st_code = Column(String(255), nullable=False, comment='过滤策略code')
    stop_loss_config = Column(String, comment='止损配置')
    schedule_config = Column(String, comment='调度配置')
    switch = Column(Integer, comment='开关')
    is_del = Column(Integer, nullable=False, default=0, comment='0: 生效 1:已删除')
    env = Column(String, comment='运行环境')
    gmt_create = Column(String, nullable=False, comment='生成时间')
    gmt_modified = Column(String, nullable=False, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'trade_pair': self.trade_pair,
            'side': self.side,
            'entry_per_trans': self.entry_per_trans,
            'loss_per_trans': self.loss_per_trans,
            'time_frame': self.time_frame,
            'entry_st_code': self.entry_st_code,
            'exit_st_code': self.exit_st_code,
            'filter_st_code': self.filter_st_code,
            'stop_loss_config': self.stop_loss_config,
            'schedule_config': self.schedule_config,
            'switch': self.switch,
            'is_del': self.is_del,
            'env': self.env,
            'gmt_create': self.gmt_create,
            'gmt_modified': self.gmt_modified
        }

    @classmethod
    def insert(cls, data: dict) -> bool:
        try:
            instance = cls(**data)
            session.add(instance)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @classmethod
    def get_by_id(cls, id: int) -> dict:
        stmt = select(cls).where(cls.id == id)
        result = session.execute(stmt).scalar_one_or_none()
        return result.to_dict() if result else None

    @classmethod
    def list_by_env(cls, env: str) -> list:
        stmt = select(cls).where(cls.env == env, cls.is_del == 0)
        results = session.execute(stmt).scalars().all()
        return [result.to_dict() for result in results]

    @classmethod
    def list_by_trade_pair(cls, trade_pair: str) -> list:
        stmt = select(cls).where(cls.trade_pair == trade_pair, cls.is_del == 0)
        results = session.execute(stmt).scalars().all()
        return [result.to_dict() for result in results]

    @classmethod
    def delete_by_id(cls, id: int) -> bool:
        try:
            stmt = update(cls).where(cls.id == id).values(is_del=1)
            session.execute(stmt)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @classmethod
    def get_all_active(cls) -> List['StrategyInstance']:
        """Get all non-deleted strategy instances"""
        return DatabaseUtils.get_db_session().query(cls).filter_by(is_del=0).all()

    @classmethod
    def get_st_instance_by_id(cls, id: int) -> 'StrategyInstance':
        strategy = session.query(StrategyInstance).filter(
            StrategyInstance.id == id,
            StrategyInstance.is_del == 0
        ).first()
        """Get strategy instance by ID"""
        return DatabaseUtils.get_db_session().query(cls).filter_by(id=id, is_del=0).first()


def get_st_instance_by_id(id: int) -> StrategyInstance:
    strategy = session.query(StrategyInstance).filter(
        StrategyInstance.id == id,
        StrategyInstance.is_del == 0
    ).first()
    """Get strategy instance by ID"""
    return DatabaseUtils.get_db_session().query(StrategyInstance).filter_by(id=id, is_del=0).first()


if __name__ == '__main__':
    session = DatabaseUtils.get_db_session()

    # 查询所有策略实例
    # st = get_st_instance_by_id(id=8)
    # print(st.name)

    st = StrategyInstance.get_st_instance_by_id(id=8)
    print(st.name)

    # # 创建一条记录
    # new_instance = StrategyInstance(
    #     name='比特币双布林带策略',
    #     trade_pair='BTC-USDT',
    #     position=1000,
    #     time_frame="4H",
    #     entry_st_code='entry_code',
    #     exit_st_code='exit_code',
    #     gmt_create=datetime.now(),
    #     gmt_modified=datetime.now()
    # )
    #
    # # 将记录添加到会话并提交
    # # 查询所有订单实例
    # st_instance_list = session.query(StrategyInstance).all()
    # for st_instance in st_instance_list:
    #     print(st_instance.id, st_instance.trade_pair)
    #
    # # 关闭会话
    # session.close()
