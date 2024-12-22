from typing import Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class SwapAlgoOrderRecord(Base):
    __tablename__ = 'swap_algo_order_record'

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
    state = Column(String(16))  # 状态
    source = Column(String(16))

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
            'source': self.source,
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
    def save_or_update_algo_order_record(cls, data: dict) -> bool:
        """
        Insert or update a single record based on ord_id.
        Args:
            data (dict): Record data including ord_id
        Returns:
            bool: Success or failure
        """
        try:
            # 获取ord_id进行查询
            ord_id = data.get('ord_id')

            if not ord_id:
                print("Error: ord_id is required for upsert operation")
                return False

            # 查找是否存在记录
            existing_record = session.query(cls).filter(
                cls.ord_id == ord_id
            ).first()

            if existing_record:
                # 如果记录存在，更新记录
                try:
                    # 排除不应更新的字段
                    update_data = {k: v for k, v in data.items()
                                   if k not in ('id', 'create_time', 'update_time')}
                    # 直接使用 update 方法而不是 setattr
                    session.query(cls).filter(cls.ord_id == ord_id).update(update_data)
                    print(f"Updating existing record for ord_id: {ord_id}")

                except Exception as e:
                    print(f"Error updating record: {e}")
                    session.rollback()
                    return False

            else:
                # 如果记录不存在，创建新记录
                try:
                    # 确保数字字段为正确类型
                    if 'sz' in data:
                        try:
                            data['sz'] = float(data['sz'])
                        except (ValueError, TypeError):
                            data['sz'] = 0.0

                    # 确保字符串字段为字符串类型
                    str_fields = ['fill_sz', 'fill_px', 'avg_px', 'lever', 'pnl', 'source']
                    for field in str_fields:
                        if field in data:
                            data[field] = str(data[field])

                    new_record = cls(**data)
                    session.add(new_record)
                    print(f"Creating new record for ord_id: {ord_id}")

                except Exception as e:
                    print(f"Error creating new record: {e}")
                    session.rollback()
                    return False

            # 提交事务
            session.commit()
            return True

        except Exception as e:
            print(f"Upsert error: {e}")
            session.rollback()
            return False
        finally:
            # 不要关闭session，因为使用的是单例模式
            pass

    @classmethod
    def insert(cls, data: dict) -> bool:
        try:
            record = cls(**data)
            session.add(record)
            session.commit()
            print(f"Creating new algo order record for: {data['cl_ord_id']}")
            return True
        except Exception as e:
            print(f"Insert error: {e}")
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

    @classmethod
    def get_by_id(cls, record_id: int):
        try:
            record = session.query(cls).filter(cls.id == record_id).first()
            return record if record else None
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
    def list_by_condition(cls, state: Optional[str], source: Optional[str]) -> list:
        """
        List records by state and source
        Args:
            state: Order state to filter by
            source: Order source to filter by
        Returns:
            list: List of matching records
        """
        try:
            # 构建查询
            query = session.query(cls)

            # 添加过滤条件
            if state:
                query = query.filter(cls.state == state)
            if source:
                query = query.filter(cls.source == source)
            # 执行查询
            results = query.all()
            return [result for result in results] if results else []
        except Exception as e:
            print(f"Error querying records by state: {e}")
            return []
        finally:
            # 使用单例模式，不关闭session
            pass

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



