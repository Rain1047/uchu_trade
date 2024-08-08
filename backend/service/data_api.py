from backend.service.utils import *


class DataAPIWrapper:

    @staticmethod
    def insert_order_details(api_response, db_model_class):
        session = DatabaseUtils.get_db_session()
        data = api_response.get('data', [])
        for order_detail_dict in data:
            # Convert dictionary to db_model_class instance
            order_detail_instance = FormatUtils.dict2dao(db_model_class, order_detail_dict)

            # Check if ord_id already exists in the database
            exists = session.query(db_model_class).filter_by(ord_id=order_detail_instance.ord_id).first()

            if exists:
                print(f"Order with ord_id {order_detail_instance.ord_id} already exists. Skipping.")
                continue

            # Add instance to the session
            session.add(order_detail_instance)
        # Commit the transaction
        session.commit()
