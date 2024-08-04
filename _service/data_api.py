import time
import okx.MarketData as MarketData
from _service.utils import *


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


class MarketAPIWrapper:
    _instance = None

    def __new__(cls, flag):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.market_data_api = MarketData.MarketAPI(flag=flag)
        return cls._instance


def query_candles_with_time_frame(trading_pair: str, flag: str, time_frame: str) -> pd.DataFrame:

    # Get the current millisecond-level timestamp
    millis_timestamp = int(time.time() * 1000)

    # Get historical candlestick data for the trading pair
    result = MarketAPIWrapper(flag).market_data_api.get_candlesticks(
        instId=trading_pair,
        bar=time_frame
    )
    return FormatUtils.dict2df(result)
