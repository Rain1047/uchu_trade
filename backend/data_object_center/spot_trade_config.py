from typing import Dict, List, Optional, Any

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from backend._utils import DatabaseUtils
from backend.data_object_center.enum_obj import EnumTradeExecuteType

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class SpotTradeConfig(Base):
    __tablename__ = 'spot_trade_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ccy = Column(String, comment='币种')
    type = Column(String, comment='类型')
    indicator = Column(String, comment='指标')
    indicator_val = Column(String, comment='指标值')
    target_price = Column(String, comment='目标价格')
    percentage = Column(String, comment='百分比')
    amount = Column(Integer, comment='金额')
    switch = Column(String, comment='开关')
    exec_nums = Column(Integer, comment='执行次数')
    is_del = Column(String, comment='是否删除')

    def to_dict(self):
        return {
            'id': self.id,
            'ccy': self.ccy,
            'type': self.type,
            'indicator': self.indicator,
            'indicator_val': self.indicator_val,
            'target_price': self.target_price,
            'percentage': self.percentage,
            'amount': self.amount,
            'switch': self.switch,
            'exec_nums': self.exec_nums,
            'is_del': self.is_del
        }

    @staticmethod
    def list_all() -> List[Dict]:
        filters = [
            SpotTradeConfig.is_del == '0',
            SpotTradeConfig.switch == '0'
        ]

        try:
            results = session.query(SpotTradeConfig).filter(*filters).all()
            return [
                {
                    'id': config.id,
                    'ccy': config.ccy,
                    'type': config.type,
                    'indicator': config.indicator,
                    'indicator_val': config.indicator_val,
                    'target_price': config.target_price,
                    'percentage': config.percentage,
                    'amount': config.amount,
                    'switch': config.switch,
                    'exec_nums': config.exec_nums,
                    'is_del': config.is_del
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def list_by_ccy_and_type(ccy, type: Optional[str] = "") -> List[Dict[str, Any]]:
        try:
            filters = [
                SpotTradeConfig.ccy == ccy,
                SpotTradeConfig.is_del == '0',
                SpotTradeConfig.exec_nums >= 0
            ]

            if type and type.strip():
                filters.append(SpotTradeConfig.type == type)

            results = session.query(SpotTradeConfig).filter(*filters).all()
            return [
                {
                    'id': config.id,
                    'ccy': config.ccy,
                    'type': config.type,
                    'indicator': config.indicator,
                    'indicator_val': config.indicator_val,
                    'target_price': config.target_price,
                    'percentage': config.percentage,
                    'amount': config.amount,
                    'switch': config.switch,
                    'exec_nums': config.exec_nums,
                    'is_del': config.is_del
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def create_or_update(config: Dict):
        try:
            if config.get('id'):
                # 更新
                session.query(SpotTradeConfig).filter(
                    SpotTradeConfig.id == config.get('id')
                ).update(config)
            else:
                # 新增
                new_config = SpotTradeConfig(
                    ccy=config.get('ccy'),
                    type=config.get('type'),
                    indicator=config.get('indicator'),
                    indicator_val=config.get('indicator_val'),
                    target_price=config.get('target_price'),
                    percentage=config.get('percentage'),
                    amount=config.get('amount'),
                    switch=config.get('switch'),
                    exec_nums=config.get('exec_nums'),
                    is_del=config.get('is_del')
                )
                session.add(new_config)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def batch_create_or_update(config_list: List[Dict[str, Any]], config_type: str):
        print(config_list)
        try:
            if not config_list or not config_type:
                print("Invalid parameters")
                return

            ccy = config_list[0].get('ccy')

            # 1. 获取数据库中当前ccy的所有未删除记录
            existing_configs = session.query(SpotTradeConfig).filter(
                SpotTradeConfig.ccy == ccy,
                SpotTradeConfig.is_del == 0,
                SpotTradeConfig.type == config_type
            ).all()

            # 2. 创建现有配置的id集合,用于后续比对
            existing_ids = {config.id for config in existing_configs}
            updating_ids = {config.get('id') for config in config_list}
            processed_ids = set()

            # 3. 遍历新配置列表,执行新增或更新
            for config in config_list:
                if config.get('id'):  # 更新已存在的记录
                    processed_ids.add(config['id'])
                    session.query(SpotTradeConfig).filter(
                        SpotTradeConfig.id == config['id']
                    ).update({
                        'type': config.get('type'),
                        'indicator': config.get('indicator'),
                        'indicator_val': config.get('indicator_val'),
                        'target_price': config.get('target_price'),
                        'percentage': config.get('percentage'),
                        'amount': config.get('amount'),
                        'switch': config.get('switch'),
                        'exec_nums': config.get('exec_nums'),
                        'is_del': config.get('is_del', '0')
                    })
                else:  # 新增记录
                    new_config = SpotTradeConfig(
                        ccy=config.get('ccy'),
                        type=config.get('type'),
                        indicator=config.get('indicator'),
                        indicator_val=config.get('indicator_val'),
                        target_price=config.get('target_price'),
                        percentage=config.get('percentage'),
                        amount=config.get('amount'),
                        switch=config.get('switch'),
                        exec_nums=config.get('exec_nums'),
                        is_del=config.get('is_del', '0')
                    )
                    session.add(new_config)

            # 4. 将未在新配置中出现的当前类型的旧记录标记为删除
            to_delete_ids = existing_ids - processed_ids
            if to_delete_ids:
                session.query(SpotTradeConfig).filter(
                    SpotTradeConfig.id.in_(to_delete_ids),
                    SpotTradeConfig.type == config_type  # 只删除当前类型的配置
                ).update({
                    'is_del': 1
                }, synchronize_session='fetch')

            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def update_switch(cls, id: int, switch: str) -> bool:
        """更新开关状态
        Args:
            id: 配置ID
            switch: 开关状态
        Returns:
            bool: 更新是否成功
        """
        try:
            result = session.query(cls) \
                .filter(cls.id == id) \
                .update({
                'switch': switch,
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update switch failed: {e}")
            return False

    @classmethod
    def delete_by_id(cls, id: int) -> bool:
        try:
            result = session.query(cls) \
                .filter(cls.id == id) \
                .update({
                'is_del': '1'
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Delete config failed: {e}")
            return False

    @classmethod
    def minus_exec_nums(cls, id: int) -> bool:
        try:
            spot_trade_config = SpotTradeConfig.get_effective_spot_config_by_id(id=id)
            if not spot_trade_config:
                return False
            exec_nums = int(spot_trade_config.get('exec_nums'))
            if exec_nums is not None:
                result = session.query(cls) \
                    .filter(cls.id == id) \
                    .update({
                        'exec_nums': str(exec_nums - 1)
                    })
                session.commit()
                return result > 0
            else:
                return False
        except Exception as e:
            session.rollback()
            print(f"Update exec_nums failed: {e}")
            return False

    @classmethod
    def get_effective_spot_config_by_id(cls, id: int):
        filters = [cls.is_del == '0',
                   cls.id == id,
                   cls.exec_nums > 0]
        result = session.query(cls).filter(*filters).first()
        return result.to_dict() if result else None

    @classmethod
    def get_effective_and_unfinished_limit_order_configs_by_ccy(cls, ccy: str) -> List[Dict]:
        filters = [cls.is_del == 0,
                   cls.ccy == ccy,
                   cls.exec_nums > 0,
                   cls.type == EnumTradeExecuteType.LIMIT_ORDER.value
                   ]
        results = session.query(cls).filter(*filters).all()
        return [result.to_dict() for result in results]

    @classmethod
    def get_effective_and_unfinished_stop_loss_configs_by_ccy(cls, ccy: str) -> List[Dict]:
        filters = [cls.is_del == 0,
                   cls.ccy == ccy,
                   cls.exec_nums > 0,
                   cls.type == EnumTradeExecuteType.STOP_LOSS.value
                   ]
        results = session.query(cls).filter(*filters).all()
        return [result.to_dict() for result in results]

    @classmethod
    def list_configs_by_ccy_and_type(cls, ccy: str, type_: str) -> List[Dict]:
        """获取币种配置"""
        try:
            configs = session.query(cls).filter(
                cls.ccy == ccy,
                cls.type == type_,
                cls.is_del == '0'
            ).all()
            return [config.to_dict() for config in configs]
        except Exception as e:
            print(f"Query configs failed: {e}")
            return []

    @classmethod
    def get_spot_config_by_id(cls, config_id):
        filters = [cls.is_del == '0',
                   cls.id == config_id]
        result = session.query(cls).filter(*filters).first()
        return result.to_dict() if result else None


if __name__ == '__main__':
    swap = SpotTradeConfig()
    print(swap.list_all())
    # 更新开关状态
    success = SpotTradeConfig.update_switch(id=1, switch='ON')

    # 更新执行次数（自增1）
    success = SpotTradeConfig.minus_exec_nums(id=1)

    # 更新执行次数（指定值）
    success = SpotTradeConfig.minus_exec_nums(id=1, exec_nums=5)
