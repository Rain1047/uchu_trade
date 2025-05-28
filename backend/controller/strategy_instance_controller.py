from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord
from backend.schedule_center.strategy_scheduler import strategy_scheduler
from backend.strategy_center.atom_strategy.dynamic_strategy_registry import DynamicStrategyRegistry
from backend.strategy_center.atom_strategy.strategy_registry import registry
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/strategy-instance", tags=["策略实例管理"])

class CreateInstanceRequest(BaseModel):
    strategy_name: str
    entry_strategy: str
    exit_strategy: str
    filter_strategy: Optional[str] = None
    schedule_frequency: str  # 1h, 4h, 1d
    symbols: List[str]
    entry_per_trans: Optional[float] = None
    loss_per_trans: Optional[float] = None
    commission: float = 0.001

class UpdateInstanceRequest(BaseModel):
    strategy_name: Optional[str] = None
    symbols: Optional[List[str]] = None
    entry_per_trans: Optional[float] = None
    loss_per_trans: Optional[float] = None
    commission: Optional[float] = None

@router.post("/create")
def create_instance(request: CreateInstanceRequest):
    """创建策略实例"""
    try:
        # 验证策略是否存在
        if not registry.get_strategy(request.entry_strategy):
            return {"success": False, "error": f"入场策略 {request.entry_strategy} 不存在"}
        if not registry.get_strategy(request.exit_strategy):
            return {"success": False, "error": f"出场策略 {request.exit_strategy} 不存在"}
        if request.filter_strategy and not registry.get_strategy(request.filter_strategy):
            return {"success": False, "error": f"过滤策略 {request.filter_strategy} 不存在"}
        
        # 创建策略实例
        strategy_params = {
            'entry_strategy': request.entry_strategy,
            'exit_strategy': request.exit_strategy,
            'filter_strategy': request.filter_strategy
        }
        
        strategy_id = f"{request.entry_strategy}_{request.exit_strategy}_{request.schedule_frequency}"
        instance = StrategyInstance.create(
            strategy_id=strategy_id,
            strategy_name=request.strategy_name,
            strategy_type='combination',
            strategy_params=strategy_params,
            schedule_frequency=request.schedule_frequency,
            symbols=request.symbols,
            entry_per_trans=request.entry_per_trans,
            loss_per_trans=request.loss_per_trans,
            commission=request.commission
        )
        
        if instance:
            return {"success": True, "instance": instance}
        else:
            return {"success": False, "error": "创建策略实例失败"}
            
    except Exception as e:
        logger.error(f"创建策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/list")
def list_instances(status: Optional[str] = None):
    """获取策略实例列表"""
    try:
        instances = StrategyInstance.list_all(status=status)
        return {"success": True, "instances": instances}
    except Exception as e:
        logger.error(f"获取策略实例列表失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/{instance_id}")
def get_instance(instance_id: int):
    """获取策略实例详情"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if instance:
            # 获取最新执行记录
            latest_execution = StrategyExecutionRecord.get_latest_by_instance_id(instance_id)
            instance['latest_execution'] = latest_execution
            return {"success": True, "instance": instance}
        else:
            return {"success": False, "error": "策略实例不存在"}
    except Exception as e:
        logger.error(f"获取策略实例详情失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.put("/{instance_id}")
def update_instance(instance_id: int, request: UpdateInstanceRequest):
    """更新策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        # 只有停止状态的实例才能更新
        if instance['status'] != 'stopped':
            return {"success": False, "error": "只有停止状态的实例才能更新"}
        
        # 更新实例
        update_data = request.dict(exclude_unset=True)
        updated_instance = StrategyInstance.update(instance_id, **update_data)
        
        if updated_instance:
            return {"success": True, "instance": updated_instance}
        else:
            return {"success": False, "error": "更新策略实例失败"}
            
    except Exception as e:
        logger.error(f"更新策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/{instance_id}/start")
def start_instance(instance_id: int):
    """启动策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        if instance['status'] == 'running':
            return {"success": False, "error": "策略实例已经在运行中"}
        
        # 添加到调度器
        success = strategy_scheduler.add_instance_job(instance_id)
        if success:
            return {"success": True, "message": "策略实例已启动"}
        else:
            return {"success": False, "error": "启动策略实例失败"}
            
    except Exception as e:
        logger.error(f"启动策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/{instance_id}/stop")
def stop_instance(instance_id: int):
    """停止策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        if instance['status'] == 'stopped':
            return {"success": False, "error": "策略实例已经停止"}
        
        # 从调度器移除
        success = strategy_scheduler.remove_instance_job(instance_id)
        if success:
            return {"success": True, "message": "策略实例已停止"}
        else:
            return {"success": False, "error": "停止策略实例失败"}
            
    except Exception as e:
        logger.error(f"停止策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/{instance_id}/pause")
def pause_instance(instance_id: int):
    """暂停策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        if instance['status'] != 'running':
            return {"success": False, "error": "只有运行中的实例才能暂停"}
        
        # 暂停调度
        success = strategy_scheduler.pause_instance_job(instance_id)
        if success:
            return {"success": True, "message": "策略实例已暂停"}
        else:
            return {"success": False, "error": "暂停策略实例失败"}
            
    except Exception as e:
        logger.error(f"暂停策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/{instance_id}/resume")
def resume_instance(instance_id: int):
    """恢复策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        if instance['status'] != 'paused':
            return {"success": False, "error": "只有暂停的实例才能恢复"}
        
        # 恢复调度
        success = strategy_scheduler.resume_instance_job(instance_id)
        if success:
            return {"success": True, "message": "策略实例已恢复"}
        else:
            return {"success": False, "error": "恢复策略实例失败"}
            
    except Exception as e:
        logger.error(f"恢复策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.delete("/{instance_id}")
def delete_instance(instance_id: int):
    """删除策略实例"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        # 如果实例在运行中，先停止
        if instance['status'] in ['running', 'paused']:
            strategy_scheduler.remove_instance_job(instance_id)
        
        # 删除实例
        success = StrategyInstance.delete(instance_id)
        if success:
            return {"success": True, "message": "策略实例已删除"}
        else:
            return {"success": False, "error": "删除策略实例失败"}
            
    except Exception as e:
        logger.error(f"删除策略实例失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/{instance_id}/executions")
def get_instance_executions(instance_id: int, limit: int = 100):
    """获取策略实例的执行记录"""
    try:
        executions = StrategyExecutionRecord.get_by_instance_id(instance_id, limit)
        return {"success": True, "executions": executions}
    except Exception as e:
        logger.error(f"获取执行记录失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/scheduler/status")
def get_scheduler_status():
    """获取调度器状态"""
    try:
        status = strategy_scheduler.get_scheduler_status()
        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"获取调度器状态失败: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/{instance_id}/test-execution")
def test_execution(instance_id: int):
    """测试执行策略（立即执行一次）"""
    try:
        instance = StrategyInstance.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "策略实例不存在"}
        
        # 直接执行策略
        logger.info(f"测试执行策略实例 {instance_id}")
        strategy_scheduler.execute_strategy(instance_id)
        
        return {"success": True, "message": "测试执行已启动，请查看日志了解执行情况"}
        
    except Exception as e:
        logger.error(f"测试执行失败: {str(e)}")
        return {"success": False, "error": str(e)} 