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
    indicator_val = Column(String, comment='时间间隔')
    percentage = Column(String, comment='百分比')
    amount = Column(Integer, comment='金额')
    switch = Column(String, comment='开关')
    is_del = Column(String, comment='是否删除')

    @staticmethod
    def list_all() -> List[Dict]:

        try:
            results = session.query(SpotTradeConfig).all()
            return [
                {
                    'id': config.id,
                    'ccy': config.ccy,
                    'type': config.type,
                    'indicator': config.indicator,
                    'indicator_val': config.indicator_val,
                    'percentage': config.percentage,
                    'amount': config.amount,
                    'switch': config.switch,
                    'is_del': config.is_del
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def list_by_ccy_and_type(ccy, type: Optional[str] = "") -> List[Dict[str, Any]]:
        try:
            filters = [SpotTradeConfig.ccy == ccy]
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
                    'percentage': config.percentage,
                    'amount': config.amount,
                    'switch': config.switch,
                    'is_del': config.is_del
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def create_or_update(config_list):
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
                        percentage=config.get('percentage'),
                        amount=config.get('amount'),
                        switch=config.get('switch'),
                        is_del=config.get('is_del')
                    )
                    session.add(new_config)

                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


if __name__ == '__main__':
    swap = SpotTradeConfig()
    print(swap.list_all())
