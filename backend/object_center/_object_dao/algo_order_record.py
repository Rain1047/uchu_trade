from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class AlgoOrderRecord(Base):
    __tablename__ = 'algo_order_record'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 下单操作后的结果
    cl_ord_id = Column(String(32))  # 客户自定义订单ID
    ord_id = Column(String(32))  # 订单ID
    s_code = Column(String(16))  # 事件执行结果的code
    s_msg = Column(String(256))  # 执行结果消息
    ts = Column(String(32))  # 系统完成订单时间戳
    tag = Column(String(32))  # 订单标签

    # 下单时携带的参数
    attach_algo_cl_ord_id = Column(String(32))  # 附带策略订单ID
    attach_algo_ords = Column(JSON)  # 附带止盈止损信息
    st_inst_id = Column(Integer)  # 策略实例id
    symbol = Column(String(32))  # 交易对
    side = Column(String(16))  # 订单方向
    pos_side = Column(String(16))  # 开仓方向
    sz = Column(Float)  # 委托数量
    interval = Column(String(16))  # 交易策略间隔

    # 订单结果参数
    fill_sz = Column(String(64))
    fill_px = Column(String(64))
    avg_px = Column(String(64))
    lever = Column(String(16))  # 杠杆
    pnl = Column(String(32))  # 盈亏
    state = Column(String(16))

    # 通用字段
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'cl_ord_id': self.cl_ord_id,
            'ord_id': self.ord_id,
            's_code': self.s_code,
            's_msg': self.s_msg,
            'ts': self.ts,
            'tag': self.tag,
            'attach_algo_cl_ord_id': self.attach_algo_cl_ord_id,
            'attach_algo_ords': self.attach_algo_ords,
            'st_inst_id': self.st_inst_id,
            'symbol': self.symbol,
            'side': self.side,
            'pos_side': self.pos_side,
            'sz': self.sz,
            'interval': self.interval,
            'lever': self.lever,
            'fill_sz': self.fill_sz,
            'fill_px': self.fill_px,
            'avg_px': self.avg_px,
            'pnl': self.pnl,
            'state': self.state,
            'create_time': self.create_time,
            'update_time': self.update_time
        }

    @classmethod
    def insert(cls, data: dict) -> bool:
        try:
            record = cls(**data)
            session.add(record)
            session.commit()
            return True
        except Exception as e:
            print(f"Insert error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    @classmethod
    def get_by_id(cls, record_id: int) -> dict:
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            return record.to_dict() if record else None
        finally:
            session.close()

    @classmethod
    def list_by_st_inst_id(cls, st_inst_id: int) -> dict:
        try:
            results = session.query(cls).filter(cls.st_inst_id == st_inst_id).all()
            return {'strategy_list': [result.to_dict() for result in results]} if results else {'strategy_list': []}
        finally:
            session.close()

    @classmethod
    def delete_by_id(cls, record_id: int) -> bool:
        try:
            result = session.query(cls).filter(cls.id == record_id).delete()
            session.commit()
            return bool(result)
        except Exception as e:
            print(f"Delete error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    @classmethod
    def update_selective_by_id(cls, record_id: int, update_data: dict) -> bool:
        try:
            result = session.query(cls).filter(cls.id == record_id).update(update_data)
            session.commit()
            return bool(result)
        except Exception as e:
            print(f"Update error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

