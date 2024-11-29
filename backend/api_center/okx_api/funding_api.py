# funding_api_wrapper.py
import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone

import okx.Funding as Funding
from typing import Dict, Optional

import requests

from backend.decorator.decorator import add_docstring
from backend.data_center.data_object.enum_obj import *
from backend.utils.utils import ConfigUtils


class FundingAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        self.fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

    @add_docstring("获取币种列表")
    def get_currencies(self) -> Dict:
        return self.fundingAPI.get_currencies()

    @add_docstring("获取余币宝余额")
    def get_saving_balance(self, ccy: str) -> Dict:
        return self.fundingAPI.get_saving_balance(ccy=ccy)

    @add_docstring("申购赎回")
    def purchase_redempt(self, ccy: str, amt: str,
                         side: Optional[str] = EnumPurchaseRedempt.REDEMPT.value,
                         rate: Optional[str] = "0.01") -> json:
        return self._purchase_redempt(ccy=ccy, amt=amt, side=side, rate=rate)

    @staticmethod
    def _purchase_redempt(ccy: str, amt: str, side: str, rate: str) -> json:
        timestamp = get_current_timestamp()
        print(timestamp)
        method = 'POST'
        request_path = '/api/v5/finance/savings/purchase-redempt'

        url = "https://aws.okx.com" + request_path

        # 生成签名
        config = ConfigUtils.get_config()
        secret = config['secretkey']  # 替换为你的密钥
        body = json.dumps({
            'ccy': ccy,
            'amt': amt,
            'side': side,
            'rate': rate
        })
        signature = generate_signature(secret, timestamp, method, request_path, body)

        print(f"signature: {signature}")

        headers = {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': config['apikey'],  # 替换为你的访问密钥
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-PASSPHRASE': config['passphrase'],  # 替换为你的访问密码
            'OK-ACCESS-TIMESTAMP': timestamp,
            # 'x-simulated-trading': '1'
        }

        response = requests.post(url, data=body, headers=headers)
        print(f"response: {response.json()}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text}")  # 打印错误信息
            response.raise_for_status()  # 引发异常以便调试
            return response.text  # 返回响应的文本以便调试


def get_current_timestamp():
    # 获取当前时间，并转为 UTC 时区
    now = datetime.now(timezone.utc)
    # 格式化为 ISO 8601 格式，包含毫秒
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def generate_signature(secret, timestamp, method, request_path, body=''):
    # 构建待签名的字符串
    message = f"{timestamp}{method}{request_path}{body}"
    # 生成 HMAC SHA256 签名
    signature = hmac.new(
        key=secret.encode(),  # 使用 secret 密钥
        msg=message.encode(),  # 消息字符串
        digestmod=hashlib.sha256  # 使用 SHA-256 算法
    ).digest()  # 生成字节
    # 将签名结果进行 Base64 编码
    return base64.b64encode(signature).decode()  # 返回字符串


if __name__ == '__main__':
    print("")

    # result = purchase_redempt(ccy='USDT', amt='10', side='redempt', rate='1.00')
    # print(result)
