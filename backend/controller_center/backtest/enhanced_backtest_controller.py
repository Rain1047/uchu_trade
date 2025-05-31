#!/usr/bin/env python3
"""
增强回测系统API控制器
提供策略列表、交易对列表、回测执行等接口
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.backtest_center.enhanced_backtest_runner import EnhancedBacktestRunner
from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager
from backend.data_object_center.enhanced_backtest_record import EnhancedBacktestRecord
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
    backtest_period: Optional[str] = None  # 添加回测时间段：1m/3m/1y
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


async def run_backtest_async(record_id: int, request: BacktestRequest):
    """异步运行回测"""
    try:
        # 更新状态为分析中
        EnhancedBacktestRecord.update_status(record_id, 'analyzing')
        
        # 创建回测运行器
        runner = EnhancedBacktestRunner()
        
        # 计算开始和结束日期（根据backtest_period）
        start_date = None
        end_date = None
        if request.backtest_period:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            if request.backtest_period == '1m':
                start_date = end_date - timedelta(days=30)
            elif request.backtest_period == '3m':
                start_date = end_date - timedelta(days=90)
            elif request.backtest_period == '1y':
                start_date = end_date - timedelta(days=365)
            
            # 转换为字符串格式
            start_date = start_date.strftime('%Y-%m-%d') if start_date else None
            end_date = end_date.strftime('%Y-%m-%d') if end_date else None
        
        # 执行回测
        results = runner.run_complete_backtest(
            entry_strategy=request.entry_strategy,
            exit_strategy=request.exit_strategy,
            filter_strategy=request.filter_strategy,
            symbols=request.symbols,
            timeframe=request.timeframe,
            initial_cash=request.initial_cash,
            risk_percent=request.risk_percent,
            commission=request.commission,
            start_date=start_date,
            end_date=end_date,
            save_to_db=request.save_to_db,
            description=request.description
        )
        
        if results.get('success'):
            # 解析结果并更新数据库
            summary = results.get('summary')
            if summary:
                # 计算每个交易对的详细结果
                symbol_results = []
                for result in summary.individual_results:
                    symbol_result = {
                        'symbol': result.symbol,
                        'total_trades': result.total_trades,
                        'winning_trades': result.winning_trades,
                        'losing_trades': result.losing_trades,
                        'win_rate': result.win_rate * 100 if result.win_rate <= 1 else result.win_rate,
                        'total_profit': result.total_return * result.initial_value,
                        'total_return': result.total_return,
                        'avg_win': result.avg_win,
                        'avg_loss': result.avg_loss,
                        'profit_loss_ratio': result.avg_win / abs(result.avg_loss) if result.avg_loss != 0 else 0,
                        'sharpe_ratio': result.sharpe_ratio,
                        'max_drawdown': result.max_drawdown
                    }
                    symbol_results.append(symbol_result)
                
                # 计算整体统计
                total_trades = sum(r['total_trades'] for r in symbol_results)
                winning_trades = sum(r['winning_trades'] for r in symbol_results)
                losing_trades = sum(r['losing_trades'] for r in symbol_results)
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                total_return = summary.avg_return
                
                # 计算平均盈利和亏损
                total_win_profit = sum(r.get('avg_win', 0) * r.get('winning_trades', 0) for r in symbol_results)
                total_loss_profit = sum(r.get('avg_loss', 0) * r.get('losing_trades', 0) for r in symbol_results)
                
                avg_win_profit = (total_win_profit / winning_trades) if winning_trades > 0 else 0
                avg_loss_profit = (total_loss_profit / losing_trades) if losing_trades > 0 else 0
                profit_loss_ratio = (avg_win_profit / abs(avg_loss_profit)) if avg_loss_profit != 0 else 0
                
                # 更新结果
                EnhancedBacktestRecord.update_results(record_id, {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'total_return': total_return,
                    'avg_win_profit': avg_win_profit,
                    'avg_loss_profit': avg_loss_profit,
                    'profit_loss_ratio': profit_loss_ratio,
                    'symbol_results': symbol_results,
                    'config_key': results.get('config_key')
                })
                
                # 更新状态为完成
                EnhancedBacktestRecord.update_status(record_id, 'completed')
            else:
                EnhancedBacktestRecord.update_status(record_id, 'failed', '回测结果为空')
        else:
            EnhancedBacktestRecord.update_status(record_id, 'failed', results.get('error', '未知错误'))
            
    except Exception as e:
        logger.error(f"异步回测执行失败: {str(e)}")
        EnhancedBacktestRecord.update_status(record_id, 'failed', str(e))


@router.post("/api/enhanced-backtest/run")
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
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
        
        # 创建回测记录
        record_data = {
            'entry_strategy': request.entry_strategy,
            'exit_strategy': request.exit_strategy,
            'filter_strategy': request.filter_strategy,
            'symbols': request.symbols,
            'timeframe': request.timeframe,
            'backtest_period': request.backtest_period,
            'initial_cash': request.initial_cash,
            'risk_percent': request.risk_percent,
            'commission': request.commission,
            'status': 'running',
            'start_time': datetime.now(),
            'description': request.description
        }
        
        record = EnhancedBacktestRecord.create(record_data)
        if not record:
            raise HTTPException(status_code=500, detail='创建回测记录失败')
        
        # 在后台异步执行回测
        background_tasks.add_task(run_backtest_async, record.id, request)
        
        logger.info(f"开始执行回测 #{record.id}: {request.entry_strategy} + {request.exit_strategy}")
        
        return {
            'success': True,
            'message': '回测已开始执行',
            'record_id': record.id
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回测执行异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f'回测执行异常: {str(e)}')


@router.get("/api/enhanced-backtest/records")
async def get_backtest_records(status: Optional[str] = None):
    """获取回测记录列表"""
    try:
        records = EnhancedBacktestRecord.list_all(status=status)
        
        # 转换为前端需要的格式
        formatted_records = []
        for record in records:
            formatted_record = record.to_dict()
            # 确保win_rate是0-100的百分比
            if formatted_record.get('win_rate') and formatted_record['win_rate'] <= 1:
                formatted_record['win_rate'] = formatted_record['win_rate'] * 100
            formatted_records.append(formatted_record)
        
        return {
            'success': True,
            'records': formatted_records,
            'total': len(formatted_records)
        }
        
    except Exception as e:
        logger.error(f"获取回测记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'获取回测记录失败: {str(e)}')


@router.get("/api/enhanced-backtest/record/{record_id}")
async def get_backtest_detail(record_id: int):
    """获取回测详情"""
    try:
        record = EnhancedBacktestRecord.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail='回测记录不存在')
        
        # 转换为前端需要的格式
        data = record.to_dict()
        
        # 确保symbol_results中的数据格式正确
        if data.get('symbol_results'):
            for result in data['symbol_results']:
                # 确保win_rate是百分比格式
                if result.get('win_rate') and result['win_rate'] <= 1:
                    result['win_rate'] = result['win_rate'] * 100
        
        return {
            'success': True,
            'data': data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'获取回测详情失败: {str(e)}')


@router.get("/api/enhanced-backtest/history")
async def get_backtest_history():
    """获取回测历史记录"""
    try:
        # 获取已完成的回测记录
        records = EnhancedBacktestRecord.list_all(status='completed', limit=50)
        
        return {
            'success': True,
            'history': [r.to_dict() for r in records],
            'total': len(records)
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
        
        # 获取回测记录统计
        summary_stats = EnhancedBacktestRecord.get_summary_stats()
        
        stats = {
            'total_strategies': len(strategies),
            'entry_strategies': len([s for s in strategies if s.get('type') == 'entry']),
            'exit_strategies': len([s for s in strategies if s.get('type') == 'exit']),
            'filter_strategies': len([s for s in strategies if s.get('type') == 'filter']),
            'total_symbols': len(symbols),
            'available_timeframes': ['1h', '4h', '1d'],
            'backtest_stats': summary_stats
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


def run_backtest_core(**kwargs):
    """
    核心回测函数，供其他模块调用
    
    参数与BacktestRequest相同：
    - entry_strategy: str
    - exit_strategy: str  
    - filter_strategy: Optional[str]
    - symbols: List[str]
    - timeframe: str
    - initial_cash: float
    - risk_percent: float
    - commission: float
    - save_to_db: bool
    - description: str
    """
    try:
        # 创建回测运行器
        runner = EnhancedBacktestRunner()
        
        # 执行回测
        results = runner.run_complete_backtest(**kwargs)
        
        return results
        
    except Exception as e:
        logger.error(f"回测执行失败: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        } 