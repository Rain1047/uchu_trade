from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import json

from backend._utils import LogConfig, DatabaseUtils
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.schedule_center.strategy_scheduler import strategy_scheduler

logger = LogConfig.get_logger(__name__)

router = APIRouter(prefix="/api/strategy-instance", tags=["strategy-instance"])


class CreateInstanceRequest(BaseModel):
    strategy_id: str
    strategy_name: str
    strategy_type: str
    strategy_params: dict
    schedule_frequency: str
    symbols: List[str]
    entry_per_trans: float | None = None
    loss_per_trans: float | None = None
    commission: float = 0.001


@router.get("/list")
async def list_instances():
    """获取策略实例列表"""
    try:
        instances = StrategyInstance.list_all()
        return {
            'success': True,
            'data': instances,
            'total': len(instances)
        }
    except Exception as e:
        logger.error(f"获取策略实例列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_instance(request: CreateInstanceRequest):
    """创建策略实例"""
    try:
        # 调用StrategyInstance的create方法
        instance = StrategyInstance.create(
            strategy_id=request.strategy_id,
            strategy_name=request.strategy_name,
            strategy_type=request.strategy_type,
            strategy_params=request.strategy_params,
            schedule_frequency=request.schedule_frequency,
            symbols=request.symbols,
            entry_per_trans=request.entry_per_trans,
            loss_per_trans=request.loss_per_trans,
            commission=request.commission
        )
        
        if instance:
            return {
                'success': True,
                'data': {'id': instance['id']}
            }
        else:
            raise HTTPException(status_code=400, detail="创建策略实例失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建策略实例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}")
async def get_instance(instance_id: int):
    """获取策略实例详情"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="策略实例不存在")
        
        return {
            'success': True,
            'data': instance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略实例详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}/executions")
async def get_instance_executions(instance_id: int):
    """获取策略执行记录"""
    try:
        # 尝试导入执行记录模块
        try:
            from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord
            records = StrategyExecutionRecord.get_by_instance_id(instance_id, limit=100)
            return {
                'success': True,
                'data': records,
                'total': len(records)
            }
        except ImportError:
            # 如果模块不存在，返回空数据
            return {
                'success': True,
                'data': [],
                'total': 0
            }
    except Exception as e:
        logger.error(f"获取策略执行记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{instance_id}/start")
async def start_instance(instance_id: int):
    """启动策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="策略实例不存在")
        
        if instance['status'] == 'running':
            raise HTTPException(status_code=400, detail="策略已在运行中")
        
        # 启动策略
        strategy_scheduler.start_strategy(instance_id)
        
        # 更新状态
        StrategyInstance.update_status(instance_id, 'running')
        
        return {'success': True, 'message': '策略已启动'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{instance_id}/stop")
async def stop_instance(instance_id: int):
    """停止策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="策略实例不存在")
        
        # 停止策略
        strategy_scheduler.stop_strategy(instance_id)
        
        # 更新状态
        StrategyInstance.update_status(instance_id, 'stopped')
        
        return {'success': True, 'message': '策略已停止'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停止策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{instance_id}/pause")
async def pause_instance(instance_id: int):
    """暂停策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="策略实例不存在")
        
        if instance['status'] != 'running':
            raise HTTPException(status_code=400, detail="只能暂停运行中的策略")
        
        # 暂停策略
        strategy_scheduler.pause_strategy(instance_id)
        
        # 更新状态
        StrategyInstance.update_status(instance_id, 'paused')
        
        return {'success': True, 'message': '策略已暂停'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"暂停策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{instance_id}/resume")
async def resume_instance(instance_id: int):
    """恢复策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="策略实例不存在")
        
        if instance['status'] != 'paused':
            raise HTTPException(status_code=400, detail="只能恢复暂停中的策略")
        
        # 恢复策略
        strategy_scheduler.resume_strategy(instance_id)
        
        # 更新状态
        StrategyInstance.update_status(instance_id, 'running')
        
        return {'success': True, 'message': '策略已恢复运行'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"恢复策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{instance_id}")
async def delete_instance(instance_id: int):
    """删除策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="策略实例不存在")
        
        if instance['status'] == 'running':
            raise HTTPException(status_code=400, detail="不能删除运行中的策略")
        
        # 删除实例
        StrategyInstance.delete(instance_id)
        
        return {'success': True, 'message': '策略已删除'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 