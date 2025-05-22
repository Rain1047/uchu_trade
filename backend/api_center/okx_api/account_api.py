# account_api_wrapper.py

import okx.Account as Account
from typing import Dict, Optional
from backend._decorators import add_docstring
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

class AccountAPIWrapper:
    def __init__(self, apikey, secretkey, passphrase, flag):
        logger.info(f"初始化AccountAPIWrapper - flag: {flag}")
        self.accountAPI = Account.AccountAPI(
            api_key=apikey,
            api_secret_key=secretkey,
            passphrase=passphrase,
            use_server_time=False,
            flag=flag,
            debug=True,  # 启用debug模式以获取更多信息
        )

    @add_docstring("获取账户余额")
    def get_account_balance(self) -> Dict:
        try:
            logger.info("开始获取账户余额")
            response = self.accountAPI.get_account_balance()
            logger.info(f"获取账户余额响应: {response}")
            if response.get('code') != '0':
                logger.error(f"获取账户余额失败 - 错误码: {response.get('code')}, 错误信息: {response.get('msg')}")
            return response
        except Exception as e:
            logger.error(f"获取账户余额时发生异常: {str(e)}", exc_info=True)
            raise

    @add_docstring("账户持仓信息 - 期货交易")
    def get_positions(self, instType='', instId: Optional[str] = '') -> Dict:
        try:
            logger.info(f"获取持仓信息 - instType: {instType}, instId: {instId}")
            response = self.accountAPI.get_positions(instId=instId, instType=instType)
            logger.info(f"获取持仓信息响应: {response}")
            return response
        except Exception as e:
            logger.error(f"获取持仓信息时发生异常: {str(e)}", exc_info=True)
            raise

    @add_docstring("账户历史持仓信息")
    def get_positions_history(self, instType: Optional[str] = '', instId: Optional[str] = '',
                              mgnMode: Optional[str] = '', type: Optional[str] = '',
                              posId: Optional[str] = '', after: Optional[str] = '',
                              before: Optional[str] = '', limit: Optional[str] = '') -> Dict:
        try:
            logger.info(f"获取历史持仓信息 - instType: {instType}, instId: {instId}")
            response = self.accountAPI.get_positions_history(instType=instType, instId=instId, mgnMode=mgnMode, type=type,
                                                     posId=posId, after=after, before=before, limit=limit)
            logger.info(f"获取历史持仓信息响应: {response}")
            return response
        except Exception as e:
            logger.error(f"获取历史持仓信息时发生异常: {str(e)}", exc_info=True)
            raise

    @add_docstring("账户账单流水")
    def get_account_bills_archive(self) -> Dict:
        try:
            logger.info("获取账户账单流水")
            response = self.accountAPI.get_account_bills_archive()
            logger.info(f"获取账户账单流水响应: {response}")
            return response
        except Exception as e:
            logger.error(f"获取账户账单流水时发生异常: {str(e)}", exc_info=True)
            raise


if __name__ == '__main__':
    pass
