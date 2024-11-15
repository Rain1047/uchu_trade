# spread_api_wrapper.py

import okx.SpreadTrading as SpreadTrading
from typing import Optional, Dict
from backend.utils.decorator import add_docstring


class SpreadAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.spreadAPI = SpreadTrading.SpreadTradingAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取订单详情")
    def get_order_details(self, clOrdId: Optional[str], ordId: Optional[str]) -> Dict:
        return self.spreadAPI.get_order_details(clOrdId=clOrdId, ordId=ordId)
