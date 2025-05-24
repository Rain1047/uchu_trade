from backend.backtest_center.backtest_main import backtest_main
from backend.data_object_center.backtest_record import BacktestRecord
from backend.data_object_center.backtest_result import BacktestResult
from backend.data_object_center.symbol_instance import SymbolInstance
from backend.data_object_center.st_instance import StrategyInstance
from backend._utils import DatabaseUtils
import json
import logging
import numpy as np
from typing import Dict, List

# 配置日志
logger = logging.getLogger(__name__)


class BacktestService:

    @staticmethod
    def list_strategies() -> list:
        session = DatabaseUtils.get_db_session()
        try:
            strategies = session.query(StrategyInstance).filter(StrategyInstance.is_del == 0).all()
            return [{
                'id': s.id,
                'name': s.name,
                'trade_pair': s.trade_pair,
                'time_frame': s.time_frame,
                'side': s.side,
                'entry_per_trans': s.entry_per_trans,
                'loss_per_trans': s.loss_per_trans,
                'entry_st_code': s.entry_st_code,
                'exit_st_code': s.exit_st_code,
                'filter_st_code': s.filter_st_code,
                'schedule_config': json.loads(s.schedule_config) if s.schedule_config else {},
                'stop_loss_config': json.loads(s.stop_loss_config) if s.stop_loss_config else {},
                'switch': s.switch,
                'gmt_create': s.gmt_create,
                'gmt_modified': s.gmt_modified
            } for s in strategies]
        except Exception as e:
            logger.error(f"获取策略列表失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def list_key(strategy_id: str) -> List[str]:
        """获取回测记录列表"""
        session = None
        try:
            session = DatabaseUtils.get_db_session()
            results = session.query(BacktestResult).filter(
                BacktestResult.strategy_id == strategy_id
            ).order_by(BacktestResult.test_finished_time.desc()).all()
            
            # 在关闭会话前获取所有需要的数据
            keys = [str(result.back_test_result_key) for result in results]
            logger.info(f"成功获取回测记录列表: {strategy_id}")
            return keys
        except Exception as e:
            logger.error(f"获取回测记录列表失败: {str(e)}")
            return []
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    logger.error(f"关闭数据库会话失败: {str(e)}")

    @staticmethod
    def _safe_int(value, default: int = 0) -> int:
        try:
            if value is None or isinstance(value, bytes):
                return default
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_float(value, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bytes):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_str(value, default: str = "") -> str:
        try:
            if value is None or isinstance(value, bytes):
                return default
            return str(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def get_backtest_detail(key: str) -> Dict:
        """根据回测结果 key 返回详情（结果指标 + 交易记录）"""
        session = DatabaseUtils.get_db_session()
        try:
            result_obj: BacktestResult | None = (
                session.query(BacktestResult)
                .filter(BacktestResult.back_test_result_key == key)
                .first()
            )
            if result_obj is None:
                logger.error(f"未找到回测结果: {key}")
                return {}

            # -------- 在 session 关闭前将 ORM 对象转换为普通 dict --------
            result_dict = {
                "symbol": BacktestService._safe_str(result_obj.symbol),
                "strategy_name": BacktestService._safe_str(result_obj.strategy_name),
                "test_finished_time": BacktestService._safe_str(result_obj.test_finished_time),
                "buy_signal_count": BacktestService._safe_int(result_obj.buy_signal_count),
                "sell_signal_count": BacktestService._safe_int(result_obj.sell_signal_count),
                "transaction_count": BacktestService._safe_int(result_obj.transaction_count),
                "profit_count": BacktestService._safe_int(result_obj.profit_count),
                "loss_count": BacktestService._safe_int(result_obj.loss_count),
                "profit_total_count": BacktestService._safe_float(result_obj.profit_total_count),
                "profit_average": BacktestService._safe_float(result_obj.profit_average),
                "profit_rate": BacktestService._safe_float(result_obj.profit_rate),
                "strategy_id": BacktestService._safe_str(result_obj.strategy_id),
                "gmt_create": BacktestService._safe_str(result_obj.gmt_create),
                "gmt_modified": BacktestService._safe_str(result_obj.gmt_modified),
            }

            record_objs: list[BacktestRecord] = (
                session.query(BacktestRecord)
                .filter(BacktestRecord.back_test_result_key == key)
                .order_by(BacktestRecord.transaction_time)
                .all()
            )

            records_list: list[Dict] = []
            for rec in record_objs:
                records_list.append(
                    {
                        "id": BacktestService._safe_int(rec.id),
                        "back_test_result_key": BacktestService._safe_str(rec.back_test_result_key),
                        "transaction_time": BacktestService._safe_str(rec.transaction_time),
                        "transaction_result": BacktestService._safe_str(rec.transaction_result),
                        "transaction_pnl": BacktestService._safe_float(rec.transaction_pnl),
                    }
                )

            response_data = {"results": result_dict, "records": records_list}
            logger.info(
                f"成功获取回测详情: {key}, record_count={len(records_list)}"
            )
            return response_data
        except Exception as e:
            logger.error(f"获取回测详情失败: {e}")
            return {}
        finally:
            # 不关闭全局会话，避免后续请求 identity map 失效
            session.flush()

    @staticmethod
    def list_record_by_key(key: str) -> List[Dict]:
        """仅返回某回测 key 的交易记录列表"""
        session = DatabaseUtils.get_db_session()
        try:
            record_objs: list[BacktestRecord] = (
                session.query(BacktestRecord)
                .filter(BacktestRecord.back_test_result_key == key)
                .order_by(BacktestRecord.transaction_time)
                .all()
            )

            record_list = [
                {
                    "id": BacktestService._safe_int(r.id),
                    "back_test_result_key": BacktestService._safe_str(r.back_test_result_key),
                    "transaction_time": BacktestService._safe_str(r.transaction_time),
                    "transaction_result": BacktestService._safe_str(r.transaction_result),
                    "transaction_pnl": BacktestService._safe_float(r.transaction_pnl),
                }
                for r in record_objs
            ]
            logger.info(
                f"成功获取回测记录列表: {key}, record_count={len(record_list)}"
            )
            return record_list
        except Exception as e:
            logger.error(f"获取回测记录失败: {e}")
            return []
        finally:
            session.flush()

    @staticmethod
    def list_backtest_results(
        strategy_id: str = None,
        start_time: str = None,
        end_time: str = None,
        min_profit_rate: float = None,
        max_profit_rate: float = None,
        min_win_rate: float = None,
        max_win_rate: float = None,
        min_trades: int = None,
        max_trades: int = None
    ):
        results = BacktestResult.list_all()
        
        # 应用筛选条件
        filtered_results = []
        for result in results:
            # 策略ID筛选
            if strategy_id and result.strategy_id != strategy_id:
                continue
                
            # 时间范围筛选
            if start_time and result.test_finished_time < start_time:
                continue
            if end_time and result.test_finished_time > end_time:
                continue
                
            # 收益率范围筛选
            if min_profit_rate is not None and result.profit_rate < min_profit_rate:
                continue
            if max_profit_rate is not None and result.profit_rate > max_profit_rate:
                continue
                
            # 胜率范围筛选
            win_rate = result.profit_count / result.transaction_count if result.transaction_count > 0 else 0
            if min_win_rate is not None and win_rate < min_win_rate:
                continue
            if max_win_rate is not None and win_rate > max_win_rate:
                continue
                
            # 交易次数范围筛选
            if min_trades is not None and result.transaction_count < min_trades:
                continue
            if max_trades is not None and result.transaction_count > max_trades:
                continue
                
            filtered_results.append(result.to_dict())
            
        return filtered_results

    @staticmethod
    def _convert_numpy_types(obj):
        """递归转换numpy类型为Python原生类型"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: BacktestService._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [BacktestService._convert_numpy_types(item) for item in obj]
        else:
            return obj

    @staticmethod
    def run_backtest(st_instance_id):
        try:
            # 运行回测
            results = backtest_main(st_instance_id)
            
            # 转换numpy类型
            results = BacktestService._convert_numpy_types(results)
            
            # 获取回测记录
            records = BacktestService.list_record_by_key(results['key'])
            
            # 获取回测详情
            details = BacktestService.get_backtest_detail(results['key'])
            
            # 返回完整的数据结构
            return {
                'success': True,
                'data': {
                    'results': results,  # 基本指标
                    'records': records,  # 交易记录
                    'details': details,  # 详细统计
                    'key': results['key']  # 回测标识
                }
            }
        except Exception as e:
            logger.error(f"运行回测失败: {str(e)}")
            return {
                'success': False,
                'message': f"运行回测失败: {str(e)}"
            }


if __name__ == '__main__':
    result = BacktestService.get_backtest_detail('BTC-USDT_ST8_202412022210')
    print({
        "success": True,
        "data": result
    })
