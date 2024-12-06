import json
from datetime import datetime
from backend.utils.utils import DatabaseUtils
from backend.object_center.object_dao.st_instance import StInstance
from backend.object_center.strategy.strategy_request import StrategyCreateOrUpdateRequest


class StrategyService:
    @staticmethod
    def create_strategy(request: StrategyCreateOrUpdateRequest) -> dict:
        session = DatabaseUtils.get_db_session()
        try:
            # 创建新的策略实例
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            strategy = StInstance(
                name=request.name,
                trade_pair=request.trade_pair,
                time_frame=request.time_frame,
                side=request.side,
                entry_per_trans=float(request.entry_per_trans),
                loss_per_trans=float(request.loss_per_trans),
                entry_st_code=request.entry_st_code,
                exit_st_code=request.exit_st_code,
                filter_st_code=request.filter_st_code,
                # 将字典转换为JSON字符串存储
                schedule_config=json.dumps(request.schedule_config),
                stop_loss_config=json.dumps(request.stop_loss_config),
                switch=1,  # 默认开启
                is_del=0,  # 默认未删除
                env='dev',  # 可以根据需要设置环境
                gmt_create=current_time,
                gmt_modified=current_time
            )

            # 添加到数据库
            session.add(strategy)
            session.commit()

            return {
                "success": True,
                "data": strategy.id,
                "message": "策略创建成功"
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"创建策略失败: {str(e)}",
                "data": None
            }
        finally:
            session.close()

    @staticmethod
    def list_strategies(page_num: int = 1, page_size: int = 10) -> dict:
        session = DatabaseUtils.get_db_session()
        try:
            # 构建查询
            query = session.query(StInstance).filter(StInstance.is_del == 0)

            # 获取总数
            total_count = query.count()

            # 分页
            offset = (page_num - 1) * page_size
            strategies = query.order_by(StInstance.gmt_create.desc()) \
                .limit(page_size) \
                .offset(offset) \
                .all()

            # 转换为字典列表
            items = []
            for strategy in strategies:
                item = {
                    'id': strategy.id,
                    'name': strategy.name,
                    'trade_pair': strategy.trade_pair,
                    'time_frame': strategy.time_frame,
                    'side': strategy.side,
                    'entry_per_trans': strategy.entry_per_trans,
                    'loss_per_trans': strategy.loss_per_trans,
                    'entry_st_code': strategy.entry_st_code,
                    'exit_st_code': strategy.exit_st_code,
                    'filter_st_code': strategy.filter_st_code,
                    'schedule_config': json.loads(strategy.schedule_config) if strategy.schedule_config else {},
                    'stop_loss_config': json.loads(strategy.stop_loss_config) if strategy.stop_loss_config else {},
                    'switch': strategy.switch,
                    'gmt_create': strategy.gmt_create,
                    'gmt_modified': strategy.gmt_modified
                }
                items.append(item)

            return {
                "success": True,
                "data": {
                    "items": items,
                    "total_count": total_count,
                    "page_size": page_size,
                    "page_num": page_num
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"获取策略列表失败: {str(e)}",
                "data": None
            }
        finally:
            session.close()

    @staticmethod
    def update_strategy(strategy_id: int, request: StrategyCreateOrUpdateRequest) -> dict:
        session = DatabaseUtils.get_db_session()
        try:
            # 查找策略
            strategy = session.query(StInstance).filter(
                StInstance.id == strategy_id,
                StInstance.is_del == 0
            ).first()

            if not strategy:
                return {
                    "success": False,
                    "message": f"策略不存在或已删除: {strategy_id}",
                    "data": None
                }

            # 更新字段
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            strategy.name = request.name
            strategy.trade_pair = request.trade_pair
            strategy.time_frame = request.time_frame
            strategy.side = request.side
            strategy.entry_per_trans = float(request.entry_per_trans)
            strategy.loss_per_trans = float(request.loss_per_trans)
            strategy.entry_st_code = request.entry_st_code
            strategy.exit_st_code = request.exit_st_code
            strategy.filter_st_code = request.filter_st_code
            strategy.schedule_config = json.dumps(request.schedule_config)
            strategy.stop_loss_config = json.dumps(request.stop_loss_config)
            strategy.gmt_modified = current_time

            session.commit()

            return {
                "success": True,
                "data": strategy.id,
                "message": "策略更新成功"
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"更新策略失败: {str(e)}",
                "data": None
            }
        finally:
            session.close()

    @staticmethod
    def delete_strategy(strategy_id: int) -> dict:
        session = DatabaseUtils.get_db_session()
        try:
            # 查找策略
            strategy = session.query(StInstance).filter(
                StInstance.id == strategy_id,
                StInstance.is_del == 0
            ).first()

            if not strategy:
                return {
                    "success": False,
                    "message": f"策略不存在或已删除: {strategy_id}",
                    "data": None
                }

            # 软删除：更新 is_del 字段
            strategy.is_del = 1
            strategy.gmt_modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            session.commit()

            return {
                "success": True,
                "message": "策略删除成功",
                "data": strategy_id
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"删除策略失败: {str(e)}",
                "data": None
            }
        finally:
            session.close()

    @staticmethod
    def toggle_strategy_status(strategy_id: int, active: bool) -> dict:
        session = DatabaseUtils.get_db_session()
        try:
            strategy = session.query(StInstance).filter(
                StInstance.id == strategy_id,
                StInstance.is_del == 0
            ).first()

            if not strategy:
                return {
                    "success": False,
                    "message": f"策略不存在或已删除: {strategy_id}",
                    "data": None
                }

            # 更新开关状态
            strategy.switch = 1 if active else 0
            strategy.gmt_modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            session.commit()

            return {
                "success": True,
                "message": f"策略状态已{'启用' if active else '禁用'}",
                "data": {
                    "id": strategy_id,
                    "switch": strategy.switch
                }
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"更新策略状态失败: {str(e)}",
                "data": None
            }
        finally:
            session.close()

    @staticmethod
    def get_strategy_config():
        return None
