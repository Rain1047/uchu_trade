from typing import Dict, List, Optional, Any

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from backend._utils import DatabaseUtils

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

    @staticmethod
    def list_all() -> List[Dict]:
        filters = [
            SpotTradeConfig.is_del == '0'
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
                SpotTradeConfig.exec_nums > 0
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
                    'exec_nums':config.exec_nums,
                    'is_del': config.is_del
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def create_or_update(config_list: List[Dict[str, Any]]):
        try:
            if config_list and len(config_list) > 0:
                ccy = config_list[0].get('ccy')
                # 删除已存在配置
                session.query(SpotTradeConfig).filter(
                    SpotTradeConfig.ccy == ccy
                ).delete()

                # 批量新增配置
                for config in config_list:
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

    @staticmethod
    def update_spot_config_exec_nums(config: dict) -> bool:
        try:
            exec_nums = config.get('exec_nums')
            if not exec_nums:
                SpotTradeConfig.delete_by_id(id=config.get('id'))
            else:
                update = exec_nums - 1
                if update <= 0:
                    SpotTradeConfig.delete_by_id(id=config.get('id'))
                SpotTradeConfig.update_exec_nums(id=config.get('id'), exec_nums=update)
            return True
        except Exception as e:
            print(f"Update exec_nums failed: {e}")
            return False

    @classmethod
    def update_exec_nums(cls, id: int, exec_nums: int = None) -> bool:
        """更新执行次数
        Args:
            id: 配置ID
            exec_nums: 指定的执行次数，如果为None则自增1
        Returns:
            bool: 更新是否成功
        """
        try:
            if exec_nums is None:
                # 自增1
                record = session.query(cls).filter(cls.id == id).first()
                if not record:
                    return False
                exec_nums = (record.exec_nums or 0) + 1

            result = session.query(cls) \
                .filter(cls.id == id) \
                .update({
                'exec_nums': exec_nums
            })
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Update exec_nums failed: {e}")
            return False


if __name__ == '__main__':
    swap = SpotTradeConfig()
    print(swap.list_all())
    # 更新开关状态
    success = SpotTradeConfig.update_switch(id=1, switch='ON')

    # 更新执行次数（自增1）
    success = SpotTradeConfig.update_exec_nums(id=1)

    # 更新执行次数（指定值）
    success = SpotTradeConfig.update_exec_nums(id=1, exec_nums=5)
