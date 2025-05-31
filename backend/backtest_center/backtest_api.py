from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from backend.data_object_center.backtest_config import BacktestConfig, BacktestResult, BacktestSummary
from backend.backtest_center.universal_backtest_engine import UniversalBacktestEngine
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

router = APIRouter()
backtest_engine = UniversalBacktestEngine()

# 存储正在进行的回测任务
active_backtests: Dict[str, Dict[str, Any]] = {}

class BacktestRequest(BaseModel):
    """回测请求模型"""
    entry_strategy: str = Field(..., description="入场策略代码")
    exit_strategy: str = Field(..., description="出场策略代码")
    filter_strategy: Optional[str] = Field(None, description="过滤策略代码")
    symbols: List[str] = Field(..., description="交易对列表")
    timeframe: str = Field(..., description="时间框架")
    initial_cash: float = Field(10000.0, description="初始资金")
    risk_percent: float = Field(1.0, description="风险比例")
    commission: float = Field(0.001, description="手续费率")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    description: Optional[str] = Field(None, description="回测描述")
    tags: List[str] = Field(default_factory=list, description="标签")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="策略参数")

class BacktestResponse(BaseModel):
    """回测响应模型"""
    config_key: str
    status: str
    message: str
    progress: Optional[float] = None
    result: Optional[BacktestSummary] = None

@router.post("/backtest", response_model=BacktestResponse)
async def start_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """启动回测"""
    try:
        # 创建回测配置
        config = BacktestConfig(
            entry_strategy=request.entry_strategy,
            exit_strategy=request.exit_strategy,
            filter_strategy=request.filter_strategy,
            symbols=request.symbols,
            timeframe=request.timeframe,
            initial_cash=request.initial_cash,
            risk_percent=request.risk_percent,
            commission=request.commission,
            start_date=request.start_date,
            end_date=request.end_date,
            description=request.description,
            tags=request.tags,
            parameters=request.parameters
        )
        
        # 生成配置键
        config_key = config.generate_key()
        
        # 检查是否已有相同配置的回测
        if config_key in active_backtests:
            return BacktestResponse(
                config_key=config_key,
                status="running",
                message="回测正在进行中",
                progress=active_backtests[config_key].get("progress", 0)
            )
        
        # 创建回测任务
        active_backtests[config_key] = {
            "status": "running",
            "progress": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 在后台运行回测
        background_tasks.add_task(run_backtest_task, config, config_key)
        
        return BacktestResponse(
            config_key=config_key,
            status="started",
            message="回测已启动",
            progress=0
        )
        
    except Exception as e:
        logger.error(f"启动回测失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/backtest/{config_key}", response_model=BacktestResponse)
async def get_backtest_status(config_key: str):
    """获取回测状态"""
    if config_key not in active_backtests:
        raise HTTPException(status_code=404, detail="回测任务不存在")
        
    task_info = active_backtests[config_key]
    return BacktestResponse(
        config_key=config_key,
        status=task_info["status"],
        message=task_info.get("message", ""),
        progress=task_info.get("progress", 0),
        result=task_info.get("result")
    )

@router.get("/backtest", response_model=List[BacktestResponse])
async def list_backtests():
    """列出所有回测任务"""
    return [
        BacktestResponse(
            config_key=key,
            status=info["status"],
            message=info.get("message", ""),
            progress=info.get("progress", 0),
            result=info.get("result")
        )
        for key, info in active_backtests.items()
    ]

@router.delete("/backtest/{config_key}")
async def cancel_backtest(config_key: str):
    """取消回测任务"""
    if config_key not in active_backtests:
        raise HTTPException(status_code=404, detail="回测任务不存在")
        
    if active_backtests[config_key]["status"] != "running":
        raise HTTPException(status_code=400, detail="只能取消正在运行的回测任务")
        
    active_backtests[config_key]["status"] = "cancelled"
    active_backtests[config_key]["message"] = "回测已取消"
    
    return {"message": "回测已取消"}

async def run_backtest_task(config: BacktestConfig, config_key: str):
    """在后台运行回测任务"""
    try:
        logger.info(f"开始回测任务: {config_key}")
        
        # 运行回测
        result = backtest_engine.run_backtest(config)
        
        # 更新任务状态
        active_backtests[config_key].update({
            "status": "completed",
            "progress": 100,
            "message": "回测完成",
            "result": result
        })
        
        logger.info(f"回测任务完成: {config_key}")
        
    except Exception as e:
        logger.error(f"回测任务失败: {str(e)}")
        active_backtests[config_key].update({
            "status": "failed",
            "message": f"回测失败: {str(e)}"
        })
        
    finally:
        # 清理任务（可选）
        # del active_backtests[config_key]
        pass 