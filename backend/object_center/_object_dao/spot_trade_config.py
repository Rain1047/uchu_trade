from typing import Dict, List, Optional, Any

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from backend._utils import DatabaseUtils

Base = declarative_base()


class SpotTradeConfig(Base):
    __tablename__ = 'swap_trade_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ccy = Column(String, comment='币种')
    type = Column(String, comment='类型')
    signal = Column(String, comment='指标')
    interval = Column(String, comment='时间间隔')
    percentage = Column(String, comment='百分比')
    amount = Column(String, comment='金额')


    @staticmethod
    def list_all() -> List[Dict]:
        session = DatabaseUtils.get_db_session()
        try:
            results = session.query(SpotTradeConfig).all()
            return [
                {
                    'id': config.id,
                    'ccy': config.ccy,
                    'type': config.type,
                    'signal': config.signal,
                    'interval': config.interval,
                    'percentage': config.percentage,
                    'amount': config.amount
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def list_by_ccy_and_type(ccy, type: Optional[str] = "") -> List[Dict[str, Any]]:
        session = DatabaseUtils.get_db_session()
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
                    'signal': config.signal,
                    'interval': config.interval,
                    'percentage': config.percentage,
                    'amount': config.amount
                }
                for config in results
            ]
        finally:
            session.close()

    @staticmethod
    def create_or_update(config_list):
        session = DatabaseUtils.get_db_session()
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
                        signal=config.get('signal'),
                        interval=config.get('interval'),
                        percentage=config.get('percentage'),
                        amount=config.get('amount'),
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
