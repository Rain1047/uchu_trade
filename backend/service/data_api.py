from backend.service.utils import *


class DataAPIWrapper:

    @staticmethod
    def insert_order_details(api_response, db_model_class):
        session = DatabaseUtils.get_db_session()
        data = api_response.get('data', [])
        for response in data:
            # Convert dictionary to db_model_class instance
            instance = FormatUtils.dict2dao(db_model_class, response)
            # Check if ord_id already exists in the database
            exists = session.query(db_model_class).filter_by(ord_id=instance.ord_id).first()

            if exists:
                print(f"Order with ord_id {instance.ord_id} already exists. Skipping.")
                continue

            # Add instance to the session
            session.add(instance)
        # Commit the transaction
        session.commit()
