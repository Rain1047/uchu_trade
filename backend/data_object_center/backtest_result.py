from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import List, Optional, TYPE_CHECKING

from backend._utils import DatabaseUtils, LogConfig

Base = declarative_base()
logger = LogConfig.get_logger(__name__)

if TYPE_CHECKING:
    from typing import TypeVar
    BacktestResultType = TypeVar('BacktestResultType', bound='BacktestResult')

class BacktestResult(Base):
    __tablename__ = 'backtest_result'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    back_test_result_key = Column(String, comment='回测结果FK')
    symbol = Column(String, comment='交易对')
    strategy_id = Column(String, comment='策略实例id')
    strategy_name = Column(String, comment='策略实例名称')
    test_finished_time = Column(String, comment='运行时间')
    buy_signal_count = Column(Integer, comment='买入信号次数')
    sell_signal_count = Column(Integer, comment='卖出信号次数')
    transaction_count = Column(Integer, comment='交易次数')
    profit_count = Column(Integer, comment='获利次数')
    loss_count = Column(Integer, comment='损失次数')
    profit_total_count = Column(Float, comment='总收益')
    profit_average = Column(Float, comment='平均收益')
    profit_rate = Column(Float, comment='收益率')
    gmt_create = Column(String, nullable=False, comment='生成时间')
    gmt_modified = Column(String, nullable=False, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'back_test_result_key': self.back_test_result_key,
            'symbol': self.symbol,
            'strategy_id': self.strategy_id,
            'strategy_name': self.strategy_name,
            'test_finished_time': self.test_finished_time,
            'buy_signal_count': self.buy_signal_count,
            'sell_signal_count': self.sell_signal_count,
            'transaction_count': self.transaction_count,
            'profit_count': self.profit_count,
            'loss_count': self.loss_count,
            'profit_total_count': self.profit_total_count,
            'profit_average': self.profit_average,
            'profit_rate': self.profit_rate,
            'gmt_create': self.gmt_create,
            'gmt_modified': self.gmt_modified
        }

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def create(session: Session, data: dict) -> 'BacktestResult':
        """创建新的回测结果"""
        try:
            result = BacktestResult(**data)
            session.add(result)
            return result
        except Exception as e:
            logger.error(f"创建回测结果失败: {e}")
            raise

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def get_by_key(session: Session, key: str) -> Optional['BacktestResult']:
        """根据回测结果键获取回测结果"""
        stmt = select(BacktestResult).where(BacktestResult.back_test_result_key == key)
        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def list_all(session: Session) -> List[dict]:
        """获取所有回测结果"""
        stmt = select(BacktestResult)
        results = session.execute(stmt).scalars().all()
        return [result.to_dict() for result in results]

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def delete_by_key(session: Session, key: str) -> bool:
        """删除指定回测结果键的记录"""
        try:
            stmt = delete(BacktestResult).where(BacktestResult.back_test_result_key == key)
            session.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"删除回测结果失败: {e}")
            raise

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def update(session: Session, key: str, data: dict) -> bool:
        """更新回测结果"""
        try:
            result = session.query(BacktestResult).filter(
                BacktestResult.back_test_result_key == key
            ).first()
            
            if result:
                for key, value in data.items():
                    setattr(result, key, value)
                return True
            return False
        except Exception as e:
            logger.error(f"更新回测结果失败: {e}")
            raise

    @staticmethod
    @DatabaseUtils.execute_in_transaction
    def list_key_by_strategy(session: Session, strategy_id: str) -> List[str]:
        """根据策略ID获取回测结果键列表"""
        results = session.scalars(
            select(BacktestResult)
            .where(BacktestResult.strategy_id == strategy_id)
            .order_by(BacktestResult.id.desc())
        ).all()
        return [str(result.back_test_result_key) for result in results]


if __name__ == '__main__':
    result = BacktestResult.list_key_by_strategy('8')
    print(result)

    result = BacktestResult.get_by_key(key='BTC-USDT_ST8_202412022210')
    print(result.to_dict())

