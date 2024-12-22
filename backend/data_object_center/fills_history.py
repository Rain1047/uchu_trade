from sqlalchemy import Column, Integer, String, or_
from sqlalchemy.ext.declarative import declarative_base

from backend.controller_center.trade.trade_request import UpdateNoteRequest
from backend._utils import DatabaseUtils, FormatUtils

Base = declarative_base()
session = DatabaseUtils.get_db_session()


class FillsHistory(Base):
    __tablename__ = 'fills_history'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    inst_type = Column(String, comment='产品类型')
    inst_id = Column(String, comment='产品ID')
    trade_id = Column(String, comment='最新成交ID')
    ord_id = Column(String, comment='订单ID')
    cl_ord_id = Column(String, comment='用户自定义订单ID')
    bill_id = Column(String, comment='账单ID')
    sub_type = Column(String, comment='成交类型')
    tag = Column(String, comment='订单标签')
    fill_px = Column(String, comment='最新成交价格')
    fill_sz = Column(String, comment='最新成交数量')
    fill_idx_px = Column(String, comment='交易执行时的指数价格')
    fill_pnl = Column(String, comment='最新成交收益')
    fill_px_vol = Column(String, comment='成交时的隐含波动率')
    fill_px_usd = Column(String, comment='成交时的期权价格（USD）')
    fill_mark_vol = Column(String, comment='成交时的标记波动率')
    fill_fwd_px = Column(String, comment='成交时的远期价格')
    fill_mark_px = Column(String, comment='成交时的标记价格')
    side = Column(String, comment='订单方向（买/卖）')
    pos_side = Column(String, comment='持仓方向（多/空）')
    exec_type = Column(String, comment='流动性方向')
    fee_ccy = Column(String, comment='交易手续费币种')
    fee = Column(String, comment='手续费金额')
    ts = Column(String, comment='成交明细产生时间（Unix时间戳）')
    fill_time = Column(String, comment='成交时间')
    fee_rate = Column(String, comment='手续费费率')
    note = Column(String, comment='交易备注')

    @classmethod
    def update_note(cls, request: UpdateNoteRequest):
        if request.note is None:
            request.note = ''
        session.query(cls).filter(
            cls.id == request.id
        ).update({
            'note': request.note
        })
        session.commit()

    @classmethod
    def insert(cls, api_response):
        data = api_response.get('data', [])

        for response in data:
            # Convert dictionary to db_model_class instance
            instance = FormatUtils.dict2dao(cls, response)
            # Initialize the list of conditions
            conditions = []
            # Check and append conditions if attributes exist and are not None
            if hasattr(instance, 'ord_id') and instance.ord_id is not None:
                conditions.append(cls.ord_id == instance.ord_id)
            if hasattr(instance, 'cl_ord_id') and instance.cl_ord_id is not None:
                conditions.append(cls.cl_ord_id == instance.cl_ord_id)
            # Execute query if there are conditions
            if conditions:
                exists = session.query(cls).filter(or_(*conditions)).first()
                if exists:
                    print(f"Record with ord_id {instance.ord_id} already exists. Skipping.")
                    continue

            # Add instance to the session
            session.add(instance)
        # Commit the transaction
        session.commit()

    @classmethod
    def list_page(cls, request) -> dict:
        """分页查询成交历史记录
        Args:
            request: 包含分页参数的请求对象
                - pageSize: 每页条数
                - pageNum: 页码
                - inst_id: 产品ID（可选）
                - fill_start_time: 开始时间（可选）
                - fill_end_time: 结束时间（可选）
        Returns:
            dict: 分页结果
        """
        try:
            # 构建基础查询
            query = session.query(cls)

            # 应用过滤条件
            if request.inst_id and request.inst_id.strip():
                query = query.filter(cls.inst_id.like(f'%{request.inst_id}%'))

            if request.fill_start_time and request.fill_start_time.strip():
                query = query.filter(cls.fill_time >= request.fill_start_time)

            if request.fill_end_time and request.fill_end_time.strip():
                query = query.filter(cls.fill_time <= request.fill_end_time)

            # 排序
            query = query.order_by(cls.fill_time.desc())

            # 计算总记录数
            total_count = query.count()

            # 应用分页
            offset = (request.pageNum - 1) * request.pageSize
            results = query.limit(request.pageSize).offset(offset).all()

            # 转换结果为字典格式
            items = [FormatUtils.dao2dict(item) for item in results]

            return {
                "success": True,
                "data": {
                    "items": items,
                    "total_count": total_count,
                    "page_size": request.pageSize,
                    "page_num": request.pageNum
                }
            }

        except Exception as e:
            logger.error(f"Error in list_page: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }


if __name__ == '__main__':
    request = UpdateNoteRequest(id=28, note='测试')
    FillsHistory.update_note(request)
