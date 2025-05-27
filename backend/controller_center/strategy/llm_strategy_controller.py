#!/usr/bin/env python3
"""
LLM策略生成和管理API控制器
支持动态创建、注册和管理策略
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.strategy_center.atom_strategy.dynamic_strategy_registry import dynamic_registry
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

router = APIRouter()


# Pydantic模型定义
class StrategyCreateRequest(BaseModel):
    strategy_name: str
    strategy_type: str  # entry/exit/filter
    strategy_side: str  # long/short
    strategy_code: str
    description: str = ""
    author: str = "LLM"
    parameters: Dict[str, Any] = {}


class StrategyStatusUpdateRequest(BaseModel):
    status: str


class StrategyValidationRequest(BaseModel):
    strategy_code: str
    strategy_type: str


@router.post("/api/llm-strategy/create")
async def create_strategy(request: StrategyCreateRequest):
    """创建新的LLM策略"""
    try:
        # 验证策略类型
        if request.strategy_type not in ['entry', 'exit', 'filter']:
            raise HTTPException(status_code=400, detail='策略类型必须是 entry、exit 或 filter')
        
        # 验证策略方向
        if request.strategy_side not in ['long', 'short']:
            raise HTTPException(status_code=400, detail='策略方向必须是 long 或 short')
        
        # 检查策略名称是否已存在
        db_data = dynamic_registry.get_strategy_database()
        if request.strategy_name in db_data.get('strategies', {}):
            raise HTTPException(status_code=400, detail=f'策略名称已存在: {request.strategy_name}')
        
        # 注册策略
        success = dynamic_registry.register_llm_strategy(
            strategy_name=request.strategy_name,
            strategy_type=request.strategy_type,
            strategy_side=request.strategy_side,
            strategy_code=request.strategy_code,
            description=request.description,
            author=request.author,
            parameters=request.parameters
        )
        
        if success:
            logger.info(f"成功创建LLM策略: {request.strategy_name}")
            return {
                'success': True,
                'message': f'策略 {request.strategy_name} 创建成功',
                'strategy_name': request.strategy_name
            }
        else:
            raise HTTPException(status_code=500, detail='策略创建失败，请检查代码格式')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建策略失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.get("/api/llm-strategy/list")
async def list_strategies():
    """获取所有LLM策略列表"""
    try:
        # 获取策略数据库
        db_data = dynamic_registry.get_strategy_database()
        strategies = db_data.get('strategies', {})
        
        # 格式化返回数据
        strategy_list = []
        for name, info in strategies.items():
            strategy_list.append({
                'name': name,
                'type': info.get('type'),
                'side': info.get('side'),
                'description': info.get('description'),
                'author': info.get('author'),
                'created_at': info.get('created_at'),
                'status': info.get('status', 'active'),
                'parameters': info.get('parameters', {})
            })
        
        # 按创建时间排序
        strategy_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {
            'success': True,
            'strategies': strategy_list,
            'total': len(strategy_list)
        }
        
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.get("/api/llm-strategy/detail/{strategy_name}")
async def get_strategy_detail(strategy_name: str = Path(..., description="策略名称")):
    """获取策略详细信息"""
    try:
        db_data = dynamic_registry.get_strategy_database()
        strategies = db_data.get('strategies', {})
        
        if strategy_name not in strategies:
            raise HTTPException(status_code=404, detail=f'策略不存在: {strategy_name}')
        
        strategy_info = strategies[strategy_name]
        
        # 读取策略文件内容
        file_path = strategy_info.get('file_path')
        strategy_code = ''
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    strategy_code = f.read()
            except Exception as e:
                logger.warning(f"读取策略文件失败: {str(e)}")
        
        return {
            'success': True,
            'strategy': {
                'name': strategy_name,
                'type': strategy_info.get('type'),
                'side': strategy_info.get('side'),
                'description': strategy_info.get('description'),
                'author': strategy_info.get('author'),
                'created_at': strategy_info.get('created_at'),
                'updated_at': strategy_info.get('updated_at'),
                'status': strategy_info.get('status', 'active'),
                'parameters': strategy_info.get('parameters', {}),
                'file_path': strategy_info.get('file_path'),
                'code': strategy_code
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.delete("/api/llm-strategy/delete/{strategy_name}")
async def delete_strategy(strategy_name: str = Path(..., description="策略名称")):
    """删除策略"""
    try:
        success = dynamic_registry.delete_strategy(strategy_name)
        
        if success:
            logger.info(f"成功删除策略: {strategy_name}")
            return {
                'success': True,
                'message': f'策略 {strategy_name} 删除成功'
            }
        else:
            raise HTTPException(status_code=404, detail=f'策略 {strategy_name} 不存在或删除失败')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.put("/api/llm-strategy/status/{strategy_name}")
async def update_strategy_status(
    request: StrategyStatusUpdateRequest,
    strategy_name: str = Path(..., description="策略名称")
):
    """更新策略状态"""
    try:
        if request.status not in ['active', 'inactive', 'deprecated']:
            raise HTTPException(status_code=400, detail='无效的状态值，支持: active, inactive, deprecated')
        
        success = dynamic_registry.update_strategy_status(strategy_name, request.status)
        
        if success:
            logger.info(f"成功更新策略状态: {strategy_name} -> {request.status}")
            return {
                'success': True,
                'message': f'策略 {strategy_name} 状态更新为 {request.status}'
            }
        else:
            raise HTTPException(status_code=404, detail=f'策略 {strategy_name} 不存在')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新策略状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.post("/api/llm-strategy/validate")
async def validate_strategy_code(request: StrategyValidationRequest):
    """验证策略代码"""
    try:
        # 使用动态注册器的验证方法
        is_valid = dynamic_registry._validate_strategy_code(request.strategy_code, request.strategy_type)
        
        validation_result = {
            'valid': is_valid,
            'message': '代码验证通过' if is_valid else '代码验证失败',
            'suggestions': []
        }
        
        # 添加一些验证建议
        if not is_valid:
            validation_result['suggestions'] = [
                '检查代码语法是否正确',
                '确保包含必要的函数定义',
                '验证DataFrame操作是否正确',
                '检查信号列的设置'
            ]
        
        return {
            'success': True,
            **validation_result
        }
        
    except Exception as e:
        logger.error(f"验证策略代码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'验证失败: {str(e)}')


@router.get("/api/llm-strategy/template/{strategy_type}")
async def get_strategy_template(strategy_type: str = Path(..., description="策略类型")):
    """获取策略代码模板"""
    try:
        templates = {
            'entry': {
                'name': '入场策略模板',
                'description': '基于技术指标的入场信号生成',
                'code': '''# 入场策略模板
# 初始化信号列
df['entry_sig'] = 0
df['entry_price'] = 0

# 示例：简单移动平均线交叉策略
df['sma_short'] = df['close'].rolling(window=10).mean()
df['sma_long'] = df['close'].rolling(window=20).mean()

# 生成入场信号
condition = (df['sma_short'] > df['sma_long']) & (df['sma_short'].shift(1) <= df['sma_long'].shift(1))
df.loc[condition, 'entry_sig'] = 1
df.loc[condition, 'entry_price'] = df.loc[condition, 'close']

return df''',
                'parameters': {
                    'short_window': 10,
                    'long_window': 20
                }
            },
            
            'exit': {
                'name': '出场策略模板',
                'description': '基于止损止盈的出场信号生成',
                'code': '''# 出场策略模板
# 初始化信号列
df['sell_sig'] = 0
df['sell_price'] = df['close']

# 示例：简单止损策略
for i in range(1, len(df)):
    if df.iloc[:i]['entry_sig'].sum() == 0:
        continue
    
    # 找到最后一次买入
    last_buy_idx = df.iloc[:i][df.iloc[:i]['entry_sig'] == 1].index[-1]
    buy_price = df.loc[last_buy_idx, 'entry_price']
    current_price = df.iloc[i]['close']
    
    # 5%止损
    if current_price < buy_price * 0.95:
        df.iloc[i, df.columns.get_loc('sell_sig')] = 1
        df.iloc[i, df.columns.get_loc('sell_price')] = current_price

return df''',
                'parameters': {
                    'stop_loss_percent': 0.05,
                    'take_profit_percent': 0.10
                }
            },
            
            'filter': {
                'name': '过滤策略模板',
                'description': '基于趋势的信号过滤',
                'code': '''# 过滤策略模板
# 示例：趋势过滤器
df['sma_trend'] = df['close'].rolling(window=50).mean()

# 只在上升趋势中允许入场
trend_condition = df['close'] > df['sma_trend']
df.loc[~trend_condition, 'entry_sig'] = 0

return df''',
                'parameters': {
                    'trend_window': 50
                }
            }
        }
        
        template = templates.get(strategy_type)
        if not template:
            raise HTTPException(status_code=400, detail=f'不支持的策略类型: {strategy_type}')
        
        return {
            'success': True,
            'template': template,
            'strategy_type': strategy_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.get("/api/llm-strategy/export/{strategy_name}")
async def export_strategy(strategy_name: str = Path(..., description="策略名称")):
    """导出策略代码"""
    try:
        db_data = dynamic_registry.get_strategy_database()
        strategies = db_data.get('strategies', {})
        
        if strategy_name not in strategies:
            raise HTTPException(status_code=404, detail=f'策略不存在: {strategy_name}')
        
        strategy_info = strategies[strategy_name]
        file_path = strategy_info.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail='策略文件不存在')
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        return {
            'success': True,
            'strategy_name': strategy_name,
            'file_content': file_content,
            'file_path': file_path,
            'export_time': strategy_info.get('created_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出策略失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}')


@router.get("/api/llm-strategy/stats")
async def get_strategy_stats():
    """获取策略统计信息"""
    try:
        db_data = dynamic_registry.get_strategy_database()
        strategies = db_data.get('strategies', {})
        
        # 统计信息
        stats = {
            'total': len(strategies),
            'by_type': {'entry': 0, 'exit': 0, 'filter': 0},
            'by_side': {'long': 0, 'short': 0},
            'by_status': {'active': 0, 'inactive': 0, 'deprecated': 0},
            'by_author': {}
        }
        
        for strategy_info in strategies.values():
            # 按类型统计
            strategy_type = strategy_info.get('type', 'unknown')
            if strategy_type in stats['by_type']:
                stats['by_type'][strategy_type] += 1
            
            # 按方向统计
            strategy_side = strategy_info.get('side', 'unknown')
            if strategy_side in stats['by_side']:
                stats['by_side'][strategy_side] += 1
            
            # 按状态统计
            status = strategy_info.get('status', 'active')
            if status in stats['by_status']:
                stats['by_status'][status] += 1
            
            # 按作者统计
            author = strategy_info.get('author', 'Unknown')
            stats['by_author'][author] = stats['by_author'].get(author, 0) + 1
        
        return {
            'success': True,
            'stats': stats,
            'metadata': db_data.get('metadata', {})
        }
        
    except Exception as e:
        logger.error(f"获取策略统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f'服务器错误: {str(e)}') 