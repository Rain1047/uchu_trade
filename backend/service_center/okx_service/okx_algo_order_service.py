import logging
from typing import Optional, List, Dict, Any

from backend._decorators import add_docstring
from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend.object_center.enum_obj import EnumAlgoOrdType

logger = logging.getLogger(__name__)


class OKXAlgoOrderService:

    def __init__(self):
        self.okx = OKXAPIWrapper()
        self.trade = self.okx.trade_api
        self.funding = self.okx.funding_api
        self.account = self.okx.account

    # [主要方法] 取消所有未成交的限价单
    @add_docstring("取消所有未成交的限价单")
    def cancel_all_algo_orders_main_task(self):
        spot_unfinished_algo_list = self.list_spot_unfinished_algo_order()
        cancel_algo_list = []
        for algo_order in spot_unfinished_algo_list:
            cancel_algo_list.append(
                {
                    'instId': algo_order.get('instId'),
                    'algoId': algo_order.get('algoId')
                }
            )
        self.cancel_spot_unfinished_algo_order(cancel_algo_list)

    # 获取现货所有未完成的止盈止损委托
    @add_docstring("获取现货所有未完成的止盈止损委托")
    def list_spot_unfinished_algo_order(self) -> List[Dict[str, Any]]:
        """
        获取未完成的现货算法订单列表

        Returns:
            List[Dict[str, Any]]: 订单列表，如果没有订单或发生错误则返回空列表
        """
        try:
            result = self.trade.order_algos_list(
                instType='SPOT',
                ordType=EnumAlgoOrdType.CONDITIONAL_OCO.value
            )

            # 检查result和data是否存在且有效
            data = result.get('data')
            if result.get('code') == '0' and data and isinstance(data, list):
                return data

            return []

        except Exception as e:
            # 记录错误日志
            logging.error(f"获取算法订单列表失败: {str(e)}")
            return []

    # 取消现货所有未完成的止盈止损和限价委托
    @add_docstring("取消现货所有未完成的止盈止损和限价委托")
    def cancel_spot_unfinished_algo_order(self, algo_orders):
        cancel_result = self.trade.cancel_algo_order(algo_orders)
        print(cancel_result)

