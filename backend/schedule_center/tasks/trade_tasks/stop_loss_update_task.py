from typing import Dict, Any, List

from backend.object_center._object_dao.account_balance import AccountBalance
from backend.object_center._object_dao.spot_trade_config import SpotTradeConfig
from backend.object_center.enum_obj import EnumAutoTradeConfigType
from backend.schedule_center.core.base_task import BaseTask, TaskResult, TaskConfig


class StopLossUpdateTask(BaseTask):

    def __init__(self, name: str = "stop_loss_update"):
        config = TaskConfig(
            timeout=180,  # 3分钟超时
            max_retries=2,
            retry_delay=5
        )
        super().__init__(name, config)

    def execute(self) -> TaskResult:
        try:
            self.logger.info("开始更新止损设置...")

            # 从前一个任务获取数据
            if not hasattr(self, 'previous_result'):
                return TaskResult(
                    success=False,
                    message="没有获取到交易数据"
                )

            trade_data = self.previous_result.data.get("trade_data", {})

            # 获取所有交易配置内容
            balance_list = AccountBalance.list_all()
            for balance in balance_list:
                if balance.get('stop_loss_switch') == 'true':
                    stop_loss_configs = SpotTradeConfig.list_by_ccy_and_type(balance.get('ccy'),
                                                                             EnumAutoTradeConfigType.STOP_LOSS.value)
                    # 执行止损更新
                    total_eq = balance.get('eq_usd')
                    update_results = self._update_stop_losses(total_eq, stop_loss_configs)
                    self.logger.info(f"成功更新{balance.get('ccy')} 的止损设置")

                if balance.get('limit_order_switch') == 'true':
                    limit_order_configs = SpotTradeConfig.list_by_ccy_and_type(balance.get('ccy'),
                                                                               EnumAutoTradeConfigType.LIMIT_ORDER.value)
                else:
                    continue

            trade_configs = SpotTradeConfig.list_all()
            if len(trade_configs) == 0:
                self.logger.info(f"当前没有交易配置")

            # 识别需要更新止损的交易对
            stop_loss_updates = self._identify_stop_loss_updates()

            return TaskResult(
                success=True,
                message="止损设置更新成功",
                data={"updates": update_results}
            )

        except Exception as e:
            self.logger.error(f"更新止损设置失败: {str(e)}", exc_info=True)
            return TaskResult(
                success=False,
                message=f"更新止损设置失败: {str(e)}"
            )

    def _identify_stop_loss_updates(self) -> List[Dict[str, Any]]:

        updates = []
        for symbol, data in trade_data.items():
            # TODO: 实现你的止损识别逻辑
            if self._needs_stop_loss_update(data):
                updates.append({
                    "symbol": symbol,
                    "current_price": data["price"],
                    "new_stop_loss": data["price"] * 0.95  # 示例: 95%止损线
                })
        return updates

    def _needs_stop_loss_update(self, data: Dict[str, Any]) -> bool:
        # TODO: 实现你的判断逻辑
        return True

    def _update_stop_losses(self, total_eq: str, configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for update in configs:
            try:
                # TODO: 实现实际的止损更新逻辑
                results.append({
                    "symbol": update["symbol"],
                    "old_stop_loss": None,  # 需要从交易所获取
                    "new_stop_loss": update["new_stop_loss"],
                    "success": True
                })
            except Exception as e:
                self.logger.error(f"更新{update['symbol']}止损失败: {str(e)}")
                results.append({
                    "symbol": update["symbol"],
                    "error": str(e),
                    "success": False
                })
        return results
