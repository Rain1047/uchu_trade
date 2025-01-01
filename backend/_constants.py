# This file contains all the OKX error codes and success code.
# TODO 后续可以用于重试
from enum import Enum


class OKX_CONSTANTS(Enum):
    SUCCESS_CODE = '0'
    # OKX ERROR CODES
    ORDER_NOT_EXIST = '51603'
    IP_NOT_INCLUDED = '50110'

    MARKET_REST = "https://www.okx.com"
    AWS_REST = "https://aws.okx.com"
