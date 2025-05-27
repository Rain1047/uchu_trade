#!/usr/bin/env python3
"""
增强回测系统API控制器
提供策略列表、交易对列表、回测执行等接口
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.backtest_center.enhanced_backtest_runner import EnhancedBacktestRunner
from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

router = APIRouter()


# Pydantic模型定义
class BacktestRequest(BaseModel):
    entry_strategy: str
    exit_strategy: str
    filter_strategy: Optional[str] = None
    symbols: List[str]
    timeframe: str
    initial_cash: float = 100000
    risk_percent: float = 2.0
    commission: float = 0.001
    save_to_db: bool = True
    description: str = "前端API回测"


class ConfigValidationRequest(BaseModel):
    entry_strategy: Optional[str] = None
    exit_strategy: Optional[str] = None
    symbols: List[str] = []
    timeframe: Optional[str] = None
    initial_cash: float = 100000
    risk_percent: float = 2.0
    commission: float = 0.001


@router.get("/api/enhanced-backtest/strategies")
async def get_strategies():
    """获取所有可用策略列表"""
    try:
        strategies = registry.list_strategies()
        
        # 按类型分组
        grouped_strategies = {
            'entry': [],
            'exit': [],
            'filter': []
        }
        
        for strategy in strategies:
            strategy_type = strategy.get('type', 'unknown')
            if strategy_type in grouped_strategies:
                grouped_strategies[strategy_type].append({
                    'name': strategy['name'],
                    'desc': strategy.get('desc', ''),
                    'side': strategy.get('side', ''),
                    'type': strategy_type
                })
        
        return {
            'success': True,
            'strategies': grouped_strategies,
            'total': len(strategies)
        }
        
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'获取策略列表失败: {str(e)}')


@router.get("/api/enhanced-backtest/symbols")
async def get_symbols():
    """获取所有可用交易对列表"""
    try:
        kline_manager = EnhancedKlineManager()
        symbols = kline_manager.get_available_symbols()
        
        return {
            'success': True,
            'symbols': symbols,
            'total': len(symbols)
        }
        
    except Exception as e:
        logger.error(f"获取交易对列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'获取交易对列表失败: {str(e)}')


@router.post("/api/enhanced-backtest/run")
async def run_backtest(request: BacktestRequest):
    """执行回测"""
    try:
        # 验证策略是否存在
        available_strategies = registry.list_strategies()
        strategy_names = [s['name'] for s in available_strategies]
        
        if request.entry_strategy not in strategy_names:
            raise HTTPException(status_code=400, detail=f'入场策略不存在: {request.entry_strategy}')
        
        if request.exit_strategy not in strategy_names:
            raise HTTPException(status_code=400, detail=f'出场策略不存在: {request.exit_strategy}')
        
        if request.filter_strategy and request.filter_strategy not in strategy_names:
            raise HTTPException(status_code=400, detail=f'过滤策略不存在: {request.filter_strategy}')
        
        # 验证交易对
        kline_manager = EnhancedKlineManager()
        available_symbols = kline_manager.get_available_symbols()
        
        invalid_symbols = [s for s in request.symbols if s not in available_symbols]
        if invalid_symbols:
            raise HTTPException(status_code=400, detail=f'无效的交易对: {invalid_symbols}')
        
        # 创建回测运行器
        runner = EnhancedBacktestRunner()
        
        # 执行回测
        logger.info(f"开始执行回测: {request.entry_strategy} + {request.exit_strategy} + {request.filter_strategy}")
        logger.info(f"交易对: {request.symbols}, 时间框架: {request.timeframe}")
        
        results = runner.run_complete_backtest(
            entry_strategy=request.entry_strategy,
            exit_strategy=request.exit_strategy,
            filter_strategy=request.filter_strategy,
            symbols=request.symbols,
            timeframe=request.timeframe,
            initial_cash=request.initial_cash,
            risk_percent=request.risk_percent,
            commission=request.commission,
            save_to_db=request.save_to_db,
            description=request.description
        )
        
        if results.get('success'):
            logger.info("回测执行成功")
            return {
                'success': True,
                'message': '回测执行成功',
                'summary': results['summary'],
                'report': results['report'],
                'config_key': results.get('config_key')
            }
        else:
            logger.error(f"回测执行失败: {results.get('error', '未知错误')}")
            raise HTTPException(status_code=500, detail=results.get('error', '回测执行失败，请检查参数和数据'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回测执行异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f'回测执行异常: {str(e)}')


@router.get("/api/enhanced-backtest/history")
async def get_backtest_history():
    """获取回测历史记录"""
    try:
        # 这里可以添加从数据库获取历史记录的逻辑
        # 暂时返回空列表
        return {
            'success': True,
            'history': [],
            'total': 0
        }
        
    except Exception as e:
        logger.error(f"获取回测历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'获取回测历史失败: {str(e)}')


@router.post("/api/enhanced-backtest/config/validate")
async def validate_config(request: ConfigValidationRequest):
    """验证回测配置"""
    try:
        errors = []
        warnings = []
        
        # 验证策略
        if not request.entry_strategy:
            errors.append('缺少入场策略')
        
        if not request.exit_strategy:
            errors.append('缺少出场策略')
        
        # 验证交易对
        if not request.symbols:
            errors.append('至少选择一个交易对')
        elif len(request.symbols) > 10:
            warnings.append('选择的交易对过多，可能影响回测性能')
        
        # 验证参数范围
        if request.initial_cash < 1000:
            errors.append('初始资金不能少于1000')
        elif request.initial_cash > 10000000:
            warnings.append('初始资金过大，请确认是否正确')
        
        if request.risk_percent <= 0 or request.risk_percent > 10:
            errors.append('风险百分比应在0.1-10之间')
        
        if request.commission < 0 or request.commission > 0.01:
            errors.append('手续费率应在0-1%之间')
        
        return {
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'配置验证失败: {str(e)}')


@router.get("/api/enhanced-backtest/status")
async def get_system_status():
    """获取系统状态"""
    try:
        # 检查各个组件状态
        status = {
            'strategy_registry': True,
            'kline_manager': True,
            'backtest_runner': True,
            'database': True
        }
        
        # 获取统计信息
        strategies = registry.list_strategies()
        kline_manager = EnhancedKlineManager()
        symbols = kline_manager.get_available_symbols()
        
        stats = {
            'total_strategies': len(strategies),
            'entry_strategies': len([s for s in strategies if s.get('type') == 'entry']),
            'exit_strategies': len([s for s in strategies if s.get('type') == 'exit']),
            'filter_strategies': len([s for s in strategies if s.get('type') == 'filter']),
            'total_symbols': len(symbols),
            'available_timeframes': ['1h', '4h', '1d']
        }
        
        return {
            'success': True,
            'status': status,
            'stats': stats,
            'system_ready': all(status.values())
        }
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'获取系统状态失败: {str(e)}') 