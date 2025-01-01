import logging
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend._constants import OKX_CONSTANTS
from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()
logger = logging.getLogger(__name__)


class FundingBalance(Base):
    __tablename__ = 'funding_balance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ccy = Column(String, comment='币种')
    bal = Column(String, comment='余额')
    frozenBal = Column(String, comment='冻结余额')
    availBal = Column(String, comment='可用余额')

    # to_dict()方法：将模型对象转换为字典
    def to_dict(self):
        return {
            'id': self.id,
            'ccy': self.ccy,
            'bal': self.bal,
            'frozenBal': self.frozenBal,
            'availBal': self.availBal,
        }

    # insert()方法：插入一条记录
    @staticmethod
    def insert(balance_dict):
        try:
            if not isinstance(balance_dict, dict):
                raise ValueError("Input must be a dictionary.")

            # 创建新记录
            new_balance = FundingBalance(**balance_dict)

            # 将新记录添加到会话并提交
            session.add(new_balance)
            session.commit()
            return True
        except Exception as e:
            session.rollback()  # 如果出错，回滚事务
            logger.error(f"Error inserting account balance: {e}")
            return False

    # get_by_id()方法：根据id查询记录
    @staticmethod
    def get_by_id(balance_id):
        try:
            result = session.query(FundingBalance).filter(FundingBalance.id == balance_id).first()
            return result.to_dict() if result else None
        except Exception as e:
            logger.error(f"Error fetching account balance by id {balance_id}: {e}")
            return None

    # list_by_{condition}方法：根据条件查询记录
    @classmethod
    def list_by_condition(cls, condition=None, value=None):
        try:
            if condition and value is not None:  # 如果条件和对应值不为空
                results = session.query(cls).filter(getattr(cls, condition) == value).all()
            else:
                results = session.query(cls).all()
            return [result.to_dict() for result in results] if results else []
        except Exception as e:
            print(f"Error fetching records by {condition}: {e}")
            return []

    # delete_by_id()方法：根据id删除记录
    @staticmethod
    def delete_by_id(balance_id):
        try:
            result = session.query(FundingBalance).filter(FundingBalance.id == balance_id).first()
            if result:
                session.delete(result)
                session.commit()
                return True
            else:
                logger.warning(f"AccountBalance with id {balance_id} not found.")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting account balance by id {balance_id}: {e}")
            return False

    # update_selective_by_id()方法：根据id更新记录（部分更新）
    @staticmethod
    def update_selective_by_id(balance_id, update_dict):
        try:
            result = session.query(FundingBalance).filter(FundingBalance.id == balance_id).first()
            if result:
                # 只更新提供的字段
                for key, value in update_dict.items():
                    if hasattr(result, key):
                        setattr(result, key, value)
                session.commit()
                return True
            else:
                logger.warning(f"AccountBalance with id {balance_id} not found.")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating account balance by id {balance_id}: {e}")
            return False

    # reset()方法：清空表格并根据新数据重置记录
    @classmethod
    def reset(cls, data):
        try:
            # Step 1: Clear all existing records
            session.query(cls).delete()
            session.commit()

            # Step 2: Insert new data only if bal > 1
            if data.get('code') == '0' and isinstance(data.get('data'), list):
                for entry in data['data']:
                    # Convert 'bal' to a float and handle conversion errors
                    try:
                        bal = float(entry.get('bal', 0))  # Default to 0 if 'bal' is not found
                    except ValueError:
                        bal = 0  # If conversion fails, assume bal is not valid (default to 0)

                    if bal > 1:
                        new_entry = cls(
                            ccy=entry.get('ccy'),
                            bal=entry.get('bal'),
                            frozenBal=entry.get('frozenBal'),
                            availBal=entry.get('availBal')
                        )
                        session.add(new_entry)
                session.commit()
                print("Funding balance reset successful")
                return True  # Indicate success
            else:
                print("Invalid data format")
                return False
        except Exception as e:
            session.rollback()
            print(f"Error resetting data: {e}")
            return False

