# public_data_api_wrapper.py

import okx.PublicData as PublicData
from typing import Optional

from backend.data_center.data_object.enum_obj import EnumUnit
from backend.utils.decorator import add_docstring


class PublicDataAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.publicAPI = PublicData.PublicAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("张币转换")
    def get_convert_contract_coin(self, instId: str, px: str, sz: str, unit: Optional[str] = EnumUnit.USDS.value):
        return self.publicAPI.get_convert_contract_coin(instId=instId, sz=sz, px=px, unit=unit)
