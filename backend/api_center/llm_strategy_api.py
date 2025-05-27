#!/usr/bin/env python3
"""
LLM策略生成和管理API
支持动态创建、注册和管理策略
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.strategy_center.atom_strategy.dynamic_strategy_registry import dynamic_registry
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

llm_strategy_bp = Blueprint('llm_strategy', __name__)


@llm_strategy_bp.route('/api/llm-strategy/create', methods=['POST'])
def create_strategy():
    """创建新的LLM策略"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['strategy_name', 'strategy_type', 'strategy_side', 'strategy_code']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要参数: {field}'
                }), 400
        
        # 提取参数
        strategy_name = data['strategy_name']
        strategy_type = data['strategy_type']  # entry/exit/filter
        strategy_side = data['strategy_side']  # long/short
        strategy_code = data['strategy_code']
        description = data.get('description', '')
        author = data.get('author', 'LLM')
        parameters = data.get('parameters', {})
        
        # 验证策略类型
        if strategy_type not in ['entry', 'exit', 'filter']:
            return jsonify({
                'success': False,
                'error': '策略类型必须是 entry、exit 或 filter'
            }), 400
        
        # 验证策略方向
        if strategy_side not in ['long', 'short']:
            return jsonify({
                'success': False,
                'error': '策略方向必须是 long 或 short'
            }), 400
        
        # 注册策略
        success = dynamic_registry.register_llm_strategy(
            strategy_name=strategy_name,
            strategy_type=strategy_type,
            strategy_side=strategy_side,
            strategy_code=strategy_code,
            description=description,
            author=author,
            parameters=parameters
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'策略 {strategy_name} 创建成功',
                'strategy_name': strategy_name
            })
        else:
            return jsonify({
                'success': False,
                'error': '策略创建失败，请检查代码格式'
            }), 500
            
    except Exception as e:
        logger.error(f"创建策略失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@llm_strategy_bp.route('/api/llm-strategy/list', methods=['GET'])
def list_strategies():
    """获取所有策略列表"""
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
                'status': info.get('status', 'active')
            })
        
        return jsonify({
            'success': True,
            'strategies': strategy_list,
            'total': len(strategy_list)
        })
        
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@llm_strategy_bp.route('/api/llm-strategy/delete/<strategy_name>', methods=['DELETE'])
def delete_strategy(strategy_name: str):
    """删除策略"""
    try:
        success = dynamic_registry.delete_strategy(strategy_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'策略 {strategy_name} 删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'策略 {strategy_name} 不存在或删除失败'
            }), 404
            
    except Exception as e:
        logger.error(f"删除策略失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@llm_strategy_bp.route('/api/llm-strategy/status/<strategy_name>', methods=['PUT'])
def update_strategy_status(strategy_name: str):
    """更新策略状态"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({
                'success': False,
                'error': '缺少状态参数'
            }), 400
        
        success = dynamic_registry.update_strategy_status(strategy_name, status)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'策略 {strategy_name} 状态更新为 {status}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'策略 {strategy_name} 不存在'
            }), 404
            
    except Exception as e:
        logger.error(f"更新策略状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@llm_strategy_bp.route('/api/llm-strategy/validate', methods=['POST'])
def validate_strategy_code():
    """验证策略代码"""
    try:
        data = request.get_json()
        
        strategy_code = data.get('strategy_code')
        strategy_type = data.get('strategy_type')
        
        if not strategy_code or not strategy_type:
            return jsonify({
                'success': False,
                'error': '缺少策略代码或策略类型'
            }), 400
        
        # 使用动态注册器的验证方法
        is_valid = dynamic_registry._validate_strategy_code(strategy_code, strategy_type)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': '代码验证通过' if is_valid else '代码验证失败'
        })
        
    except Exception as e:
        logger.error(f"验证策略代码失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'验证失败: {str(e)}'
        }), 500


@llm_strategy_bp.route('/api/llm-strategy/template/<strategy_type>', methods=['GET'])
def get_strategy_template(strategy_type: str):
    """获取策略代码模板"""
    try:
        templates = {
            'entry': '''# 入场策略模板
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
            
            'exit': '''# 出场策略模板
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
            
            'filter': '''# 过滤策略模板
# 示例：趋势过滤器
df['sma_trend'] = df['close'].rolling(window=50).mean()

# 只在上升趋势中允许入场
trend_condition = df['close'] > df['sma_trend']
df.loc[~trend_condition, 'entry_sig'] = 0

return df'''
        }
        
        template = templates.get(strategy_type)
        if not template:
            return jsonify({
                'success': False,
                'error': f'不支持的策略类型: {strategy_type}'
            }), 400
        
        return jsonify({
            'success': True,
            'template': template,
            'strategy_type': strategy_type
        })
        
    except Exception as e:
        logger.error(f"获取策略模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500 