from backend.controller_center.balance.balance_request import TradeRecordPageRequest
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

class RecordService:

    @staticmethod
    def list_config_execute_records(config_execute_history_request: TradeRecordPageRequest):
        return SpotAlgoOrderRecord.list_spot_algo_order_record_by_conditions(config_execute_history_request)

    @staticmethod
    def save_or_update_limit_order_result(config_id: str, order: dict) -> bool:
        """保存或更新限价订单结果
        Args:
            config_id: 配置ID
            order: 订单数据
        Returns:
            bool: 操作是否成功
        """
        try:
            # 设置订单来源为手动
            order['exec_source'] = 'manual'
            # 设置配置ID
            order['config_id'] = config_id
            # 保存或更新记录
            return SpotAlgoOrderRecord.insert_or_update(order)
        except Exception as e:
            logger.error(f"保存限价订单结果失败: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def save_or_update_stop_loss_result(config_id: str, order: dict) -> bool:
        """保存或更新止损订单结果
        Args:
            config_id: 配置ID
            order: 订单数据
        Returns:
            bool: 操作是否成功
        """
        try:
            # 设置订单来源为手动
            order['exec_source'] = 'manual'
            # 设置配置ID
            order['config_id'] = config_id
            # 保存或更新记录
            return SpotAlgoOrderRecord.insert_or_update(order)
        except Exception as e:
            logger.error(f"保存止损订单结果失败: {str(e)}", exc_info=True)
            return False
