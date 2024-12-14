from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from backend.utils.utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class AlgoOrdersRecord(Base):
    __tablename__ = 'algo_orders_record'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基本字段
    amend_px_on_trigger_type = Column(String(16))  # amendPxOnTriggerType
    algo_cl_ord_id = Column(String(32))  # attachAlgoClOrdId
    algo_id = Column(String(32))  # attachAlgoId
    fail_code = Column(String(32))  # failCode
    fail_reason = Column(String(256))  # failReason
    sz = Column(String(32))  # sz
    state = Column(String(16))

    # 止损相关
    sl_ord_px = Column(String(32))  # slOrdPx
    sl_trigger_px = Column(String(32))  # slTriggerPx
    sl_trigger_px_type = Column(String(16))  # slTriggerPxType
    # 止盈相关
    tp_ord_kind = Column(String(32))  # tpOrdKind
    tp_ord_px = Column(String(32))  # tpOrdPx
    tp_trigger_px = Column(String(32))  # tpTriggerPx
    tp_trigger_px_type = Column(String(16))  # tpTriggerPxType

    # 通用字段
    is_del = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'amend_px_on_trigger_type': self.amend_px_on_trigger_type,
            'algo_cl_ord_id': self.algo_cl_ord_id,
            'algo_id': self.algo_id,
            'fail_code': self.fail_code,
            'fail_reason': self.fail_reason,
            'sl_ord_px': self.sl_ord_px,
            'sl_trigger_px': self.sl_trigger_px,
            'sl_trigger_px_type': self.sl_trigger_px_type,
            'sz': self.sz,
            'state': self.state,
            'tp_ord_kind': self.tp_ord_kind,
            'tp_ord_px': self.tp_ord_px,
            'tp_trigger_px': self.tp_trigger_px,
            'tp_trigger_px_type': self.tp_trigger_px_type,
            'is_del': self.is_del,
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
    def list_by_attach_algo_cl_ord_id(cls, attach_algo_cl_ord_id: str) -> dict:
        try:
            results = session.query(cls).filter(cls.attach_algo_cl_ord_id == attach_algo_cl_ord_id).all()
            return {'attach_algo_orders_list': [result.to_dict() for result in results]} if results else {
                'attach_algo_orders_list': []}
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
    def save_attach_algo_orders_from_response(cls, attach_algo_orders: list) -> bool:
        try:
            # 遍历并保存每个订单
            for order in attach_algo_orders:
                # 构建数据字典，字段名从驼峰转为下划线
                record_data = {
                    'amend_px_on_trigger_type': order.get('amendPxOnTriggerType', '0'),
                    'algo_cl_ord_is': order.get('algoClOrdId', ''),
                    'algo_id': order.get('algoId', ''),
                    'fail_code': order.get('failCode', ''),
                    'fail_reason': order.get('failReason', ''),
                    'sl_ord_px': order.get('slOrdPx', ''),
                    'sl_trigger_px': order.get('slTriggerPx', ''),
                    'sl_trigger_px_type': order.get('slTriggerPxType', ''),
                    'sz': order.get('sz', ''),
                    'state': order.get('state', ''),
                    'tp_ord_kind': order.get('tpOrdKind', ''),
                    'tp_ord_px': order.get('tpOrdPx', ''),
                    'tp_trigger_px': order.get('tpTriggerPx', ''),
                    'tp_trigger_px_type': order.get('tpTriggerPxType', '')
                }

                # 保存到数据库
                success = AlgoOrdersRecord.insert(record_data)
                if not success:
                    print(f"Failed to save attach algo order: {order}")
                    return False

            return True

        except Exception as e:
            print(f"Save attach algo orders error: {e}")
            return False

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