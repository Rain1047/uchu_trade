from sqlalchemy import or_

from backend.service.utils import *


class DataAPIWrapper:

    @staticmethod
    def insert2db(api_response, db_model_class):
        session = DatabaseUtils.get_db_session()
        data = api_response.get('data', [])
        for response in data:
            # Convert dictionary to db_model_class instance
            instance = FormatUtils.dict2dao(db_model_class, response)
            # Check if ord_id already exists in the database
            # Initialize the list of conditions
            conditions = []

            # Check and append conditions if attributes exist and are not None
            if hasattr(instance, 'ord_id') and instance.ord_id is not None:
                conditions.append(db_model_class.ord_id == instance.ord_id)
            if hasattr(instance, 'algo_cl_ord_id') and instance.algo_cl_ord_id is not None:
                conditions.append(db_model_class.cl_ord_id == instance.algo_cl_ord_id)
            if hasattr(instance, 'algo_id') and instance.algo_id is not None:
                conditions.append(db_model_class.algo_id == instance.algo_id)

            # Execute query if there are conditions
            if conditions:
                exists = session.query(db_model_class).filter(or_(*conditions)).first()
                if exists:
                    if hasattr(instance, 'ord_id') and instance.ord_id is not None and exists.ord_id == instance.ord_id:
                        print(f"Order with ord_id {instance.ord_id} already exists. Skipping.")
                    elif hasattr(instance,
                                 'algo_cl_ord_id') and instance.algo_cl_ord_id is not None and exists.cl_ord_id == instance.algo_cl_ord_id:
                        print(f"Order with cl_ord_id {instance.algo_cl_ord_id} already exists. Skipping.")
                    elif hasattr(instance,
                                 'algo_id') and instance.algo_id is not None and exists.algo_id == instance.algo_id:
                        print(f"Order with algo_id {instance.algo_id} already exists. Skipping.")
                    continue
            # Add instance to the session
            session.add(instance)
        # Commit the transaction
        session.commit()
