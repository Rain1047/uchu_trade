from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.schedule_center.core.base_task import BaseTask, TaskResult, TaskConfig


class TradeDataFetchTask(BaseTask):
    """任务A: 获取最新交易数据并添加指标"""

    def __init__(self, name: str = "trade_data_fetch"):
        config = TaskConfig(
            timeout=300,  # 5分钟超时
            max_retries=3,
            retry_delay=10,
            required_success=True  # 必须成功才能继续链
        )
        super().__init__(name, config)

    def execute(self) -> TaskResult:
        try:
            self.logger.info("开始获取交易数据...")

            # trade_data = self.fetch_trade_data()
            data_collector = KlineDataCollector()
            res = data_collector.batch_collect_data()
            if not res.get("success"):
                return TaskResult(
                    success=False,
                    message=f"获取交易数据失败"
                )
            else:
                data_len = res.get("data")

            self.logger.info(f"成功获取交易数据: {data_len} 个交易对")

            return TaskResult(
                success=True,
                message="交易数据获取成功",
                data={"trade_data": data_len}
            )

        except Exception as e:
            self.logger.error(f"获取交易数据失败: {str(e)}", exc_info=True)
            return TaskResult(
                success=False,
                message=f"获取交易数据失败: {str(e)}"
            )


if __name__ == '__main__':
    task = TradeDataFetchTask()
    result = task.execute()
    print(result.to_dict())
