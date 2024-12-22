from typing import List

import pandas as pd

from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center.enum_obj import EnumTdMode, EnumAlgoOrdType
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService


class SpotSubTaskLimitOrder:

    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()

    # [调度子任务] 根据配置进行限价委托
    def execute_limit_order_task(self, limit_order_configs: List):
        # 获取真实的账户余额 赎回赚币-划转到交易账户
        real_account_balance = self.okx_balance_service.get_real_account_balance(ccy="USDT")

        for config in limit_order_configs:
            ccy = config.get('ccy')
            print(ccy)
            balance = AccountBalance().get_by_ccy(config.get('ccy'))
            eq = balance.get('eq')
            interval = config.get('interval')
            pct = config.get('percentage')
            amount = config.get('amount')
            # 通过sig和interval获取价格
            file_abspath = self.kline_reader.get_abspath(symbol=ccy, interval='1D')
            kline_data = pd.read_csv(f"{file_abspath}")
            target_index = config.get('signal').lower() + interval
            target_price = kline_data.iloc[-1][target_index]
            print(f"{eq},{pct}")
            if pct is not None and str(pct).strip():
                eq = str(round(float(eq) * int(pct) / 100, 6))
                print(eq)
            else:
                eq = '0'

            print(
                {
                    'instId': f"{config.get('ccy')}-USDT",
                    'tdMode': EnumTdMode.CASH.value,
                    'side': "sell",
                    'ordType': EnumAlgoOrdType.CONDITIONAL.value,
                    'sz': eq,
                    'slTriggerPx': str(target_price),  # 止损触发价格
                    'slOrdPx': '-1'
                }
            )
            result = self.trade.place_algo_order(
                instId=f"{config.get('ccy')}-USDT",
                tdMode=EnumTdMode.CASH.value,
                side="sell",
                ordType=EnumAlgoOrdType.CONDITIONAL.value,
                sz=eq,
                slTriggerPx=str()
            )
