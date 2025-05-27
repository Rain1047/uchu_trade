from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.data_object_center.backtest_config import BacktestConfig, BacktestSummary
from backend.backtest_center.universal_backtest_engine import universal_engine
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

router = APIRouter(prefix="/api/universal-backtest", tags=["Universal Backtest"])


class BacktestConfigRequest(BaseModel):
    """回测配置请求模型"""
    entry_strategy: str
    exit_strategy: str
    filter_strategy: Optional[str] = None
    symbols: List[str]
    timeframe: str = "1h"
    initial_cash: float = 100000.0
    risk_percent: float = 2.0
    commission: float = 0.001
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    strategy_params: Dict = {}
    description: Optional[str] = None


class BacktestResponse(BaseModel):
    """回测响应模型"""
    success: bool
    message: str
    config_key: Optional[str] = None
    summary: Optional[Dict] = None


@router.get("/strategies")
async def get_available_strategies():
    """获取可用的策略列表"""
    try:
        strategies = universal_engine.get_available_strategies()
        return {
            "success": True,
            "data": strategies
        }
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols")
async def get_available_symbols():
    """获取可用的交易对列表"""
    try:
        symbols = universal_engine.get_available_symbols()
        return {
            "success": True,
            "data": symbols
        }
    except Exception as e:
        logger.error(f"获取交易对列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_backtest(request: BacktestConfigRequest, background_tasks: BackgroundTasks):
    """运行回测"""
    try:
        # 验证输入
        if not request.symbols:
            raise HTTPException(status_code=400, detail="至少需要选择一个交易对")
        
        if not request.entry_strategy or not request.exit_strategy:
            raise HTTPException(status_code=400, detail="必须指定入场和出场策略")
        
        # 创建配置对象
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
            strategy_params=request.strategy_params,
            description=request.description
        )
        
        config_key = config.generate_key()
        
        # 检查是否已有缓存结果
        cached_results = universal_engine.get_cached_results()
        for cached in cached_results:
            if cached.config_key == config_key:
                return BacktestResponse(
                    success=True,
                    message="从缓存获取回测结果",
                    config_key=config_key,
                    summary=cached.to_dict()
                )
        
        # 如果是多个交易对或复杂配置，使用后台任务
        if len(request.symbols) > 3:
            background_tasks.add_task(run_backtest_background, config)
            return BacktestResponse(
                success=True,
                message=f"回测任务已启动，配置键: {config_key}。请稍后查询结果。",
                config_key=config_key
            )
        else:
            # 直接运行回测
            summary = universal_engine.run_backtest(config)
            return BacktestResponse(
                success=True,
                message="回测完成",
                config_key=config_key,
                summary=summary.to_dict()
            )
            
    except Exception as e:
        logger.error(f"运行回测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_backtest_background(config: BacktestConfig):
    """后台运行回测任务"""
    try:
        logger.info(f"开始后台回测任务: {config.get_display_name()}")
        summary = universal_engine.run_backtest(config)
        logger.info(f"后台回测任务完成: {config.generate_key()}")
    except Exception as e:
        logger.error(f"后台回测任务失败: {str(e)}")


@router.get("/results")
async def get_backtest_results():
    """获取所有回测结果"""
    try:
        results = universal_engine.get_cached_results()
        return {
            "success": True,
            "data": [result.to_dict() for result in results],
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"获取回测结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{config_key}")
async def get_backtest_result(config_key: str):
    """根据配置键获取特定回测结果"""
    try:
        results = universal_engine.get_cached_results()
        for result in results:
            if result.config_key == config_key:
                return {
                    "success": True,
                    "data": result.to_dict()
                }
        
        raise HTTPException(status_code=404, detail="未找到对应的回测结果")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/results/{config_key}")
async def delete_backtest_result(config_key: str):
    """删除特定的回测结果"""
    try:
        if config_key in universal_engine.results_cache:
            del universal_engine.results_cache[config_key]
            return {
                "success": True,
                "message": "回测结果已删除"
            }
        else:
            raise HTTPException(status_code=404, detail="未找到对应的回测结果")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除回测结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/results")
async def clear_all_results():
    """清空所有回测结果"""
    try:
        universal_engine.clear_cache()
        return {
            "success": True,
            "message": "所有回测结果已清空"
        }
    except Exception as e:
        logger.error(f"清空回测结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-test")
async def quick_backtest(request: BacktestConfigRequest):
    """快速回测 - 仅测试单个交易对"""
    try:
        if len(request.symbols) != 1:
            raise HTTPException(status_code=400, detail="快速回测只支持单个交易对")
        
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
            strategy_params=request.strategy_params,
            description=request.description
        )
        
        # 不保存到缓存的快速测试
        summary = universal_engine.run_backtest(config, save_results=False)
        
        return {
            "success": True,
            "message": "快速回测完成",
            "data": summary.to_dict()
        }
        
    except Exception as e:
        logger.error(f"快速回测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/validate")
async def validate_config(
    entry_strategy: str,
    exit_strategy: str,
    filter_strategy: Optional[str] = None,
    symbols: str = "",  # 逗号分隔的交易对列表
    timeframe: str = "1h"
):
    """验证回测配置"""
    try:
        # 解析交易对列表
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        
        # 验证策略是否存在
        available_strategies = universal_engine.get_available_strategies()
        
        errors = []
        
        # 验证入场策略
        entry_strategies = [s['name'] for s in available_strategies.get('entry', [])]
        if entry_strategy not in entry_strategies:
            errors.append(f"入场策略 '{entry_strategy}' 不存在")
        
        # 验证出场策略
        exit_strategies = [s['name'] for s in available_strategies.get('exit', [])]
        if exit_strategy not in exit_strategies:
            errors.append(f"出场策略 '{exit_strategy}' 不存在")
        
        # 验证过滤策略
        if filter_strategy:
            filter_strategies = [s['name'] for s in available_strategies.get('filter', [])]
            if filter_strategy not in filter_strategies:
                errors.append(f"过滤策略 '{filter_strategy}' 不存在")
        
        # 验证交易对
        available_symbols = universal_engine.get_available_symbols()
        for symbol in symbol_list:
            if symbol not in available_symbols:
                errors.append(f"交易对 '{symbol}' 不可用")
        
        if errors:
            return {
                "success": False,
                "errors": errors
            }
        else:
            # 生成配置预览
            config = BacktestConfig(
                entry_strategy=entry_strategy,
                exit_strategy=exit_strategy,
                filter_strategy=filter_strategy,
                symbols=symbol_list,
                timeframe=timeframe
            )
            
            return {
                "success": True,
                "message": "配置验证通过",
                "preview": {
                    "config_key": config.generate_key(),
                    "display_name": config.get_display_name(),
                    "estimated_symbols": len(symbol_list)
                }
            }
            
    except Exception as e:
        logger.error(f"验证配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 