import logging
from typing import Optional
from backend.data_object_center.fills_history import FillsHistory
from backend.controller_center.trade.trade_request import TradePageRequest, UpdateNoteRequest
from backend._constants import *
from backend.api_center.okx_api.okx_main import OKXAPIWrapper

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

okx = OKXAPIWrapper()


class TradeService:
    @staticmethod
    def get_fill_history(req: Optional[TradePageRequest] = None) -> dict:
        """获取成交历史记录
        Args:
            req: 分页请求参数
        Returns:
            dict: 分页数据结果
        """
        try:
            # 1. 从API获取最新数据并保存
            result = okx.trade.get_trade_fills_history(instType="SPOT")
            if result['code'] == OKX_CONSTANTS.SUCCESS_CODE.value:
                FillsHistory.insert(result)
            else:
                logger.error(f"Failed to get fills history: {result['code']}, {result['msg']}")

            # 2. 使用默认分页参数（如果请求为空）
            page_request = req or TradePageRequest(
                pageSize=10,
                pageNum=1
            )

            # 3. 直接使用类的分页方法
            return FillsHistory.list_page(page_request)

        except Exception as e:
            logger.error(f"Error in get_fill_history: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }

    @staticmethod
    def update_history_note(req: UpdateNoteRequest) -> bool:
        FillsHistory.update_note(req)
        return True


if __name__ == '__main__':
    result = okx.trade.get_trade_fills_history(instType="SPOT")
    print(result)

