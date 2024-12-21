from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from backend._decorators import add_docstring
from backend._utils import DatabaseUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


@add_docstring("余币宝余额")
class SavingBalance(Base):
    __tablename__ = 'saving_balance'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    amt = Column(String, comment='币种金额')
    ccy = Column(String, comment='币种')
    earnings = Column(String, comment='币种持仓收益')
    loan_amt = Column(String, comment='已出借数量')
    pending_amt = Column(String, comment='未出借数量')
    rate = Column(String, comment='币种持仓收益')
    redempt_amt = Column(String, comment='可赎回数量-已废弃')

    # Method to convert an instance to a dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'amt': self.amt,
            'ccy': self.ccy,
            'earnings': self.earnings,
            'loan_amt': self.loan_amt,
            'pending_amt': self.pending_amt,
            'rate': self.rate,
            'redempt_amt': self.redempt_amt
        }

    # Method to insert a new entry into the database
    @classmethod
    def insert(cls, data):
        try:
            new_entry = cls(**data)
            session.add(new_entry)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error inserting data: {e}")
            return False

    # Method to get a record by ID
    @classmethod
    def get_by_id(cls, record_id):
        try:
            result = session.query(cls).filter_by(id=record_id).first()
            return result.to_dict() if result else None
        except Exception as e:
            print(f"Error fetching record by ID: {e}")
            return None

    # Method to list records by a condition (e.g., list_by_ccy)
    @classmethod
    def list_by_condition(cls, condition=None, value=None):
        try:
            if condition and value is not None:  # 如果条件和对应值不为空
                # Dynamically build the query based on the condition
                results = session.query(cls).filter(getattr(cls, condition) == value).all()
            else:
                # If no condition or value is provided, return all records
                results = session.query(cls).all()

            # Return results as a list of dictionaries
            return [result.to_dict() for result in results] if results else []

        except Exception as e:
            print(f"Error fetching records by {condition}: {e}")
            return []

    # Method to delete a record by ID
    @classmethod
    def delete_by_id(cls, record_id):
        try:
            result = session.query(cls).filter_by(id=record_id).first()
            if result:
                session.delete(result)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting record by ID: {e}")
            return False

    @classmethod
    def reset(cls, data):
        try:
            # Step 1: Clear all existing records
            session.query(cls).delete()
            session.commit()

            # Step 2: Insert new data only if bal > 1
            if data.get('code') == '0' and isinstance(data.get('data'), list):
                for entry in data['data']:
                    # Check if 'bal' exists and if it's greater than 1
                    bal = entry.get('bal', 0)  # Default to 0 if 'bal' is not found
                    if bal > 1:
                        new_entry = cls(
                            amt=entry.get('amt'),
                            ccy=entry.get('ccy'),
                            earnings=entry.get('earnings'),
                            loan_amt=entry.get('loanAmt'),
                            pending_amt=entry.get('pendingAmt'),
                            rate=entry.get('rate'),
                            redempt_amt=entry.get('redemptAmt')
                        )
                        session.add(new_entry)
                session.commit()
                print("Saving balance reset successfully")
                return True  # Indicate success
            else:
                print("Invalid data format")
                return False
        except Exception as e:
            session.rollback()
            print(f"Error resetting data: {e}")
            return False



