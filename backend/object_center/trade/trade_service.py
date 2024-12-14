from typing import Optional
from backend.object_center.object_dao.fills_history import FillsHistory
from backend.object_center.trade.trade_request import TradePageRequest, UpdateNoteRequest
from backend.service.data_api import *
from backend._constants import *
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dbApi = DataAPIWrapper()
okx = OKXAPIWrapper()


class TradeService:
    @staticmethod
    def get_fill_history(req: Optional[TradePageRequest] = None) -> dict:
        """
        获取成交历史记录，支持分页查询

        Args:
            req (Optional[PageRequest]): 分页请求参数，如果为None则使用默认值

        Returns:
            dict: 包含分页数据的字典，格式如下:
            {
                "items": List[FillsHistory],
                "total_count": int,
                "page_size": int,
                "page_num": int
            }
        """
        try:
            result = okx.trade.get_trade_fills_history(instType="SPOT")
            code = result['code']
            msg = result['msg']
            if code == SUCCESS_CODE:
                dbApi.insert2db(result, FillsHistory)
            else:
                print(code, msg)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")

        # 使用默认分页参数，如果请求为空
        page_request = req or TradePageRequest(
            pageSize=10,
            pageNum=1
        )
        # 调用数据库API获取数据
        return dbApi.page(page_request, FillsHistory)

    @staticmethod
    def update_history_note(req: UpdateNoteRequest) -> bool:
        FillsHistory.update_note(req)
        return True
