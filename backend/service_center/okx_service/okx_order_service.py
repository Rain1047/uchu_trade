import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any

from backend._decorators import add_docstring
from backend._utils import SymbolFormatUtils
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend.data_object_center.spot_trade_config import SpotTradeConfig
from backend.data_object_center.swap_algo_order_record import SwapAlgoOrderRecord
from backend.data_object_center.swap_attach_algo_orders_record import SwapAttachAlgoOrdersRecord
from backend.data_object_center.enum_obj import EnumAlgoOrdType, EnumTdMode, EnumOrdType, EnumOrderState
from backend.strategy_center.strategy_result import StrategyExecuteResult

logger = logging.getLogger(__name__)


class OKXOrderService:

    def __init__(self):
        self.okx = OKXAPIWrapper()
        self.trade = self.okx.trade_api
        self.funding = self.okx.funding_api
        self.account = self.okx.account_api


    def cancel_spot_unfinished_order(self, ):
        self.trade.cancel_order()


