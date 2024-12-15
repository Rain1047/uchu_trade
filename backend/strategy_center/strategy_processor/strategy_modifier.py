import logging
from typing import Optional

from backend._utils import DatabaseUtils
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.object_center.enum_obj import EnumTradeEnv
from backend.service_center.okx_service.trade_swap import TradeSwapManager


class StrategyExecutor:
    def __init__(self, env: str = EnumTradeEnv.MARKET.value, time_frame: Optional[str] = None):
        self.env = env
        self.tf = time_frame
        self.okx_api = OKXAPIWrapper(env)
        self.trade_api = self.okx_api.trade_api
        self.trade_swap_manager = TradeSwapManager()
        self.data_collector = KlineDataCollector()
        self.session = DatabaseUtils.get_db_session()
        _setup_logging()


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
