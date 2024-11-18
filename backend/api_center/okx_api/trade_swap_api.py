# trade_api_wrapper.py
import logging

import okx.Trade as Trade
from typing import Optional, Dict, Any, List
from backend.utils.decorator import add_docstring
from backend.data_center.data_object.enum_obj import *
logger = logging.getLogger(__name__)

class TradeAPIWrapper:
    pass