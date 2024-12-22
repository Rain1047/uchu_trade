from typing import List, Optional

import pandas as pd

from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.data_center.kline_data.kline_data_reader import KlineDataReader
from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center.enum_obj import EnumTdMode, EnumAlgoOrdType, EnumSide
from backend.service_center.okx_service.okx_balance_service import OKXBalanceService
from backend.service_center.okx_service.okx_ticker_service import OKXTickerService


class SpotSubTaskStopLoss:

    def __init__(self):
        self.kline_reader = KlineDataReader()
        self.trade = OKXAPIWrapper().trade_api
        self.okx_balance_service = OKXBalanceService()
        self.okx_ticker_service = OKXTickerService()

    # [调度子任务] 止损委托
    def execute_stop_loss_task(self, config: dict, is_real: Optional[bool] = False):
        ccy = config.get('ccy')
        # 获取目标止损价格
        target_price = config.get('target_price')
        if not target_price:
            # 计算目标止损价

            # 根据indicator获取实时价格

            pass



        # 获取交易仓位
        account_balance = 0.0
        if is_real:
            account_balance = self.okx_balance_service.get_real_account_balance(ccy=ccy)
        else:
            account_balance = config.get('amount')

        amount = config.get('amount')
        if not amount:
            pct = config.get('percentage')
        else:
            sz = ''

        interval = config.get('interval')
        # 通过sig和interval获取价格
        file_abspath = self.kline_reader.get_abspath(symbol=ccy, interval='1D')
        kline_data = pd.read_csv(f"{file_abspath}")
        target_index = config.get('signal').lower() + interval
        target_price = kline_data.iloc[-1][target_index]

        if pct is not None and str(pct).strip():
            eq = str(round(float(account_balance) * int(pct) / 100, 6))
        else:
            eq = '0'



        result = self.trade.place_algo_order(
            instId=f"{config.get('ccy')}-USDT",
            tdMode=EnumTdMode.CASH.value,
            side=EnumSide.SELL.value,
            ordType=EnumAlgoOrdType.CONDITIONAL.value,
            sz=sz,
            slTriggerPx=str(target_price),  # 止损触发价格
            slOrdPx='-1'
        )
        print(result)

    def handle_real_stop_loss_task(self):
        pass


if __name__ == '__main__':
    trade = OKXAPIWrapper().trade_api
    result = trade.place_algo_order(
        instId=f"ETH-USDT",
        tdMode=EnumTdMode.CASH.value,
        side=EnumSide.SELL.value,
        ordType=EnumAlgoOrdType.CONDITIONAL.value,
        sz="0.01",
        slTriggerPx=str(3300),  # 止损触发价格
        slOrdPx='-1'
    )
    print(result)
