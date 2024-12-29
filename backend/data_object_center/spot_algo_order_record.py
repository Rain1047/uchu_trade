from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend._decorators import singleton
from backend._utils import DatabaseUtils
from backend.controller_center.balance.balance_request import TradeConfigExecuteHistory
from backend.data_object_center.enum_obj import EnumOrderState

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class SpotAlgoOrderRecord(Base):
    __tablename__ = 'spot_algo_order_record'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ccy = Column(String, comment='币种')
    type = Column(String, comment='类型')
    config_id = Column(String, comment='配置id')
    sz = Column(String, comment='仓位')
    amount = Column(String, comment='金额/USDT')
    target_price = Column(String, comment='目标价格')
    algoId = Column(String, comment='止损订单id')
    ordId = Column(String, comment='限价订单id')
    status = Column(String, comment='订单状态')
    exec_source = Column(String, comment='操作来源')
    create_time = Column(DateTime, comment='创建时间')
    update_time = Column(DateTime, comment='更新时间')

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'ccy': self.ccy,
            'type': self.type,
            'config_id': self.config_id,
            'sz': self.sz,
            'amount': self.amount,
            'target_price': self.target_price,
            'algoId': self.algoId,
            'ordId': self.ordId,
            'status': self.status,
            'exec_source': self.exec_source,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

    @classmethod
    def insert_or_update(cls, data: Dict) -> bool:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['update_time'] = current_time

            # Check if record exists by ordId or algoId
            existing_record = None
            if data.get('ordId'):
                existing_record = session.query(cls).filter(cls.ordId == data['ordId']).first()
            elif data.get('algoId'):
                existing_record = session.query(cls).filter(cls.algoId == data['algoId']).first()

            if existing_record:
                for key, value in data.items():
                    setattr(existing_record, key, value)
            else:
                data['create_time'] = current_time
                record = cls(**data)
                session.add(record)

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Insert/Update failed: {e}")
            return False

    @classmethod
    def get_by_id(cls, id: int) -> Optional[Dict]:
        """根据ID获取记录
        Args:
            id: 记录ID
        Returns:
            Optional[Dict]: 记录字典或None
        """
        try:
            result = session.query(cls).filter(cls.id == id).first()
            return result.to_dict() if result else None
        except Exception as e:
            print(f"Query failed: {e}")
            return None

    @classmethod
    def list_by_ccy(cls, ccy: str) -> List[Dict]:
        """根据币种查询记录列表
        Args:
            ccy: 币种
        Returns:
            Dict[str, List[Dict]]: 包含记录列表的字典
        """
        try:
            results = session.query(cls).filter(cls.ccy == ccy).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_by_ccy_and_status(cls, ccy: str, status: str) -> List[Dict]:
        filters = [
            SpotAlgoOrderRecord.ccy == ccy,
            SpotAlgoOrderRecord.status == status,
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_by_type(cls, type: str) -> List[Dict]:
        """根据类型查询记录列表
        Args:
            type: 订单类型
        Returns:
            Dict[str, List[Dict]]: 包含记录列表的字典
        """
        try:
            results = session.query(cls).filter(cls.type == type).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_by_status(cls, status: str) -> List[Dict]:
        """根据状态查询记录列表
        Args:
            status: 订单状态
        Returns:
            Dict[str, List[Dict]]: 包含记录列表的字典
        """
        try:
            results = session.query(cls).filter(cls.status == status).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def delete_by_id(cls, id: int) -> bool:
        """根据ID删除记录
        Args:
            id: 记录ID
        Returns:
            bool: 删除是否成功
        """
        try:
            result = session.query(cls).filter(cls.id == id).delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Delete failed: {e}")
            return False

    @classmethod
    def update_selective_by_id(cls, id: int, data: Dict) -> bool:
        """根据ID选择性更新记录
        Args:
            id: 记录ID
            data: 更新数据字典
        Returns:
            bool: 更新是否成功
        """
        try:
            data['update_time'] = datetime.now()
            result = session.query(cls).filter(cls.id == id).update(data)
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update failed: {e}")
            return False

    @classmethod
    def update_status_by_algo_id(cls, algo_id: str, status: str) -> bool:
        """根据算法订单ID更新状态
        Args:
            algo_id: 算法订单ID
            status: 新状态
        Returns:
            bool: 更新是否成功
        """
        try:
            result = session.query(cls).filter(cls.algoId == algo_id).update({
                'status': status,
                'update_time': datetime.now()
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update failed: {e}")
            return False

    @classmethod
    def update_status_by_ord_id(cls, ord_id: str, status: str) -> bool:
        """根据订单ID更新状态
        Args:
            ord_id: 订单ID
            status: 新状态
        Returns:
            bool: 更新是否成功
        """
        try:
            result = session.query(cls).filter(cls.ordId == ord_id).update({
                'status': status,
                'update_time': datetime.now()
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update failed: {e}")
            return False

    @classmethod
    def get_by_algo_id(cls, algo_id: str) -> Optional[Dict]:
        """根据算法订单ID获取记录
        Args:
            algo_id: 算法订单ID
        Returns:
            Optional[Dict]: 记录字典或None
        """
        try:
            result = session.query(cls).filter(cls.algoId == algo_id).first()
            return result.to_dict() if result else None
        except Exception as e:
            print(f"Query failed: {e}")
            return None

    @classmethod
    def get_by_ord_id(cls, ord_id: str) -> Optional[Dict]:
        """根据订单ID获取记录
        Args:
            ord_id: 订单ID
        Returns:
            Optional[Dict]: 记录字典或None
        """
        try:
            result = session.query(cls).filter(cls.ordId == ord_id).first()
            return result.to_dict() if result else None
        except Exception as e:
            print(f"Query failed: {e}")
            return None

    @classmethod
    def list_live_auto_spot_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.algoId.is_(None),
            SpotAlgoOrderRecord.ordId.isnot(None),
            SpotAlgoOrderRecord.exec_source == 'auto'
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_live_manual_spot_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.algoId.is_(None),
            SpotAlgoOrderRecord.ordId.isnot(None),
            SpotAlgoOrderRecord.exec_source == 'manual'
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_live_auto_spot_algo_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.algoId.isnot(None),
            SpotAlgoOrderRecord.ordId.is_(None),
            SpotAlgoOrderRecord.exec_source == 'auto'
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_live_manual_spot_algo_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.algoId.isnot(None),
            SpotAlgoOrderRecord.ordId.is_(None),
            SpotAlgoOrderRecord.exec_source == 'manual'
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_spot_algo_order_record_by_conditions(cls, config_execute_history_request: TradeConfigExecuteHistory):
        filters = []
        if config_execute_history_request.ccy:
            filters.append(SpotAlgoOrderRecord.ccy == config_execute_history_request.ccy)
        if config_execute_history_request.type:
            filters.append(SpotAlgoOrderRecord.type == config_execute_history_request.type)
        if config_execute_history_request.status:
            filters.append(SpotAlgoOrderRecord.status == config_execute_history_request.status)
        if config_execute_history_request.exec_source:
            filters.append(SpotAlgoOrderRecord.exec_source == config_execute_history_request.exec_source)
        if config_execute_history_request.create_time:
            try:
                # 将字符串日期转换为 datetime 对象
                create_time_dt = datetime.strptime(config_execute_history_request.create_time, "%Y-%m-%d")
                filters.append(SpotAlgoOrderRecord.create_time >= create_time_dt)
            except ValueError as e:
                raise ValueError(f"日期格式错误: {e}")

        return session.query(cls).filter(*filters).all()


if __name__ == '__main__':
    pass