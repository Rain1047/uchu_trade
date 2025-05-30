from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend._decorators import singleton
from backend._utils import DatabaseUtils
from backend.controller_center.balance.balance_request import TradeRecordPageRequest
from backend.data_object_center.enum_obj import EnumOrderState, EnumExecSource, EnumTradeExecuteType

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
    exec_price = Column(String, comment='执行价格')

    algoId = Column(String, comment='止损订单id')
    ordId = Column(String, comment='限价订单id')
    status = Column(String, comment='订单状态')
    exec_source = Column(String, comment='操作来源')
    create_time = Column(DateTime, comment='创建时间')
    update_time = Column(DateTime, comment='更新时间')
    cTime = Column(DateTime, comment='订单创建时间')
    uTime = Column(DateTime, comment='订单更新时间')

    side = Column(String, comment='订单方向')
    note = Column(String, comment='交易日志')

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
            'exec_price': self.exec_price,
            'algoId': self.algoId,
            'ordId': self.ordId,
            'status': self.status,
            'exec_source': self.exec_source,
            'side': self.side,
            'note': self.note,
            'cTime': self.cTime.strftime('%Y-%m-%d %H:%M:%S') if self.cTime else None,
            'uTime': self.uTime.strftime('%Y-%m-%d %H:%M:%S') if self.uTime else None,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
        }

    @classmethod
    def insert_or_update(cls, data: Dict) -> bool:
        try:
            # 获取有效字段
            valid_fields = {column.name for column in cls.__table__.columns}

            # 过滤并准备数据
            processed_data = {}
            for key in valid_fields:
                if key in data:
                    processed_data[key] = data[key]

            # 设置当前时间
            current_time = datetime.now()
            processed_data['update_time'] = current_time

            # 处理时间戳
            if processed_data.get('cTime'):
                processed_data['cTime'] = datetime.fromtimestamp(int(processed_data['cTime']) / 1000)
            if processed_data.get('uTime'):
                processed_data['uTime'] = datetime.fromtimestamp(int(processed_data['uTime']) / 1000)

            # 检查记录是否存在
            existing_record = None
            if processed_data.get('ordId'):
                existing_record = session.query(cls).filter(cls.ordId == processed_data['ordId']).first()
            elif processed_data.get('algoId'):
                existing_record = session.query(cls).filter(cls.algoId == processed_data['algoId']).first()

            # 更新或插入记录
            if existing_record:
                for key, value in processed_data.items():
                    setattr(existing_record, key, value)
            else:
                processed_data['create_time'] = current_time
                record = cls(**processed_data)
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
    def list_live_auto_spot_limit_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.type == EnumTradeExecuteType.LIMIT_ORDER.value,
            SpotAlgoOrderRecord.exec_source == EnumExecSource.AUTO.value
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_live_manual_limit_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.type == EnumTradeExecuteType.LIMIT_ORDER.value,
            SpotAlgoOrderRecord.exec_source == EnumExecSource.MANUAL.value
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_live_auto_stop_loss_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.type == EnumTradeExecuteType.STOP_LOSS.value,
            SpotAlgoOrderRecord.exec_source == EnumExecSource.AUTO.value
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_live_manual_spot_stop_loss_orders(cls) -> List[Dict[str, Any]]:
        filters = [
            SpotAlgoOrderRecord.status == EnumOrderState.LIVE.value,
            SpotAlgoOrderRecord.type == EnumTradeExecuteType.STOP_LOSS.value,
            SpotAlgoOrderRecord.exec_source == EnumExecSource.MANUAL.value
        ]
        try:
            results = session.query(cls).filter(*filters).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    @classmethod
    def list_spot_algo_order_record_by_conditions(cls, config_execute_history_request: TradeRecordPageRequest):
        """分页查询订单记录"""
        filters = []

        # 添加过滤条件
        if config_execute_history_request.ccy:
            filters.append(SpotAlgoOrderRecord.ccy.like(f'%{config_execute_history_request.ccy}%'))
        if config_execute_history_request.type:
            filters.append(SpotAlgoOrderRecord.type == config_execute_history_request.type)
        if config_execute_history_request.side:
            filters.append(SpotAlgoOrderRecord.side == config_execute_history_request.side)
        if config_execute_history_request.status:
            filters.append(SpotAlgoOrderRecord.status == config_execute_history_request.status)
        if config_execute_history_request.exec_source:
            filters.append(SpotAlgoOrderRecord.exec_source == config_execute_history_request.exec_source)

        # 处理时间范围
        if config_execute_history_request.begin_time and config_execute_history_request.end_time:
            try:
                begin_time_dt = datetime.strptime(config_execute_history_request.begin_time, "%Y-%m-%d")
                end_time_dt = datetime.strptime(config_execute_history_request.end_time, "%Y-%m-%d")
                filters.append(SpotAlgoOrderRecord.uTime >= begin_time_dt)
                filters.append(SpotAlgoOrderRecord.uTime <= end_time_dt)
            except ValueError as e:
                raise ValueError(f"日期格式错误: {e}")

        # 分页参数
        page_size = config_execute_history_request.pageSize or 10
        page_num = config_execute_history_request.pageNum or 1
        offset = (page_num - 1) * page_size

        # 查询总数
        total = session.query(cls).filter(*filters).count()

        # 分页查询
        results = session.query(cls) \
            .filter(*filters) \
            .order_by(SpotAlgoOrderRecord.uTime.desc()) \
            .limit(page_size) \
            .offset(offset) \
            .all()

        records = []
        for result in results:
            record_dict = result.to_dict()
            # 格式化 amount 和 exec_price
            try:
                record_dict['amount'] = format(float(record_dict['amount']), '.4f') if record_dict[
                    'amount'] else '0.0000'
                record_dict['exec_price'] = format(float(record_dict['exec_price']), '.4f') if record_dict[
                    'exec_price'] else '0.0000'
            except (ValueError, TypeError):
                # 处理可能的转换错误
                record_dict['amount'] = '0.0000'
                record_dict['exec_price'] = '0.0000'
            records.append(record_dict)

        return {
            "records": records,
            "total": total,
            "pageSize": page_size,
            "pageNum": page_num
        }

    @classmethod
    def update_status_by_order(cls, order: dict) -> bool:
        try:
            result = session.query(cls).filter(cls.ordId == order.get('ordId')).update({
                'status': order.get('state'),
                'update_time': datetime.now(),
                'cTime': order.get('cTime'),
                'uTime': order.get('uTime'),
                'exec_price': order.get('avgPrice', '')
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update failed: {e}")
            return False

    @classmethod
    def update_status_by_algo_order(cls, algo_order: dict):
        try:
            result = session.query(cls).filter(cls.ordId == algo_order.get('algoId')).update({
                'status': algo_order.get('state'),
                'update_time': datetime.now(),
                'uTime': algo_order.get('uTime'),
                'exec_price': algo_order.get('avgPrice', '')
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update failed: {e}")
            return False

    @classmethod
    def mark_canceled_by_ordId(cls, ordId):
        try:
            result = session.query(cls).filter(cls.ordId == ordId).update({
                'status': EnumOrderState.CANCELED.value,
                'update_time': datetime.now(),
                'cTime': None,
                'uTime': None,
                'exec_price': ''
            })
            session.commit()
            return result > 0
        except Exception as e:
            print(f"Update failed: {e}")
            return False

    @classmethod
    def mark_canceled_by_algoId(cls, algoId):
        try:
            result = session.query(cls).filter(cls.algoId == algoId).update({
                'status': EnumOrderState.CANCELED.value,
                'update_time': datetime.now(),
                'cTime': None,
                'uTime': None,
                'exec_price': ''
            })
            session.commit()
            return result > 0
        except Exception as e:
            print(f"Update failed: {e}")
            return False


if __name__ == '__main__':
    data = {
        'type': 'manual',
        'sz': '3.846136',
        'algoClOrdId': '',
        'algoId': '',
        'attachAlgoClOrdId': '',
        'attachAlgoOrds': [],
        'px': '136.94',
        'cTime': '1726336347482',
        'cancelSource': '',
        'cancelSourceReason': '',
        'category': 'normal',
        'ccy': '',
        'clOrdId': '',
        'fee': '-0.003846136',
        'feeCcy': 'SOL',
        'fillPx': '136.94',
        'fillSz': '3.846136',
        'fillTime': '1726336347484',
        'instId': 'SOL-USDT',
        'instType': 'SPOT',
        'isTpLimit': 'false',
        'lever': '',
        'linkedAlgoOrd': {'algoId': ''},
        'ordId': '1806367530105946112',
        'ordType': 'market',
        'pnl': '0',
        'posSide': '',
        'pxType': '',
        'pxUsd': '',
        'pxVol': '',
        'quickMgnType': '',
        'rebate': '0',
        'rebateCcy': 'USDT',
        'reduceOnly': 'false',
        'side': 'buy',
        'slOrdPx': '',
        'slTriggerPx': '',
        'slTriggerPxType': '',
        'source': '',
        'state': 'filled',
        'stpId': '',
        'stpMode': 'cancel_maker',
        'tag': '',
        'tdMode': 'cash',
        'tgtCcy': 'quote_ccy',
        'tpOrdPx': '',
        'tpTriggerPx': '',
        'tpTriggerPxType': '',
        'tradeId': '172891248',
        'uTime': '1726336347485'
    }

    # result = SpotAlgoOrderRecord.insert_or_update(data)
    # print("Insert/Update result:", result)
