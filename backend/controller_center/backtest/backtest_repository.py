from typing import Optional, List
from backend.utils.database_utils import DatabaseUtils
from backend.models.backtest_result import BacktestResult
from backend.models.backtest_record import BacktestRecord

class BacktestRepository:
    async def get_result(self, key: str) -> Optional[BacktestResult]:
        """获取回测结果"""
        session = DatabaseUtils.get_db_session()
        try:
            result = session.query(BacktestResult).filter(
                BacktestResult.back_test_result_key == key
            ).first()
            return result
        finally:
            session.close()

    async def get_records(self, key: str) -> List[BacktestRecord]:
        """获取回测记录"""
        session = DatabaseUtils.get_db_session()
        try:
            records = session.query(BacktestRecord).filter(
                BacktestRecord.back_test_result_key == key
            ).order_by(BacktestRecord.timestamp).all()
            return records
        finally:
            session.close() 