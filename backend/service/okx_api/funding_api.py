# funding_api_wrapper.py

import okx.Funding as Funding
from typing import Dict
from backend.service.decorator import add_docstring


class FundingAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取币种列表")
    def get_currencies(self) -> Dict:
        return self.fundingAPI.get_currencies()
