#!/usr/bin/env python3
"""
动态策略注册系统
支持LLM创建的策略自动注册、数据库存储和动态加载
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)


class DynamicStrategyRegistry:
    """动态策略注册器"""
    
    def __init__(self):
        self.strategy_db_file = "backend/strategy_center/atom_strategy/strategy_database.json"
        self.strategy_dir = "backend/strategy_center/atom_strategy"
        self.auto_generated_dir = "backend/strategy_center/atom_strategy/auto_generated"
        
        # 确保自动生成策略目录存在
        os.makedirs(self.auto_generated_dir, exist_ok=True)
        
        # 初始化策略数据库
        self._init_strategy_database()
    
    def _init_strategy_database(self):
        """初始化策略数据库文件"""
        if not os.path.exists(self.strategy_db_file):
            initial_data = {
                "strategies": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            self._save_strategy_database(initial_data)
    
    def _load_strategy_database(self) -> Dict:
        """加载策略数据库"""
        try:
            with open(self.strategy_db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载策略数据库失败: {str(e)}")
            return {"strategies": {}, "metadata": {}}
    
    def _save_strategy_database(self, data: Dict):
        """保存策略数据库"""
        try:
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.strategy_db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存策略数据库失败: {str(e)}")
    
    def register_llm_strategy(self, 
                            strategy_name: str,
                            strategy_type: str,  # 'entry', 'exit', 'filter'
                            strategy_side: str,  # 'long', 'short'
                            strategy_code: str,
                            description: str = "",
                            author: str = "LLM",
                            parameters: Dict = None) -> bool:
        """
        注册LLM生成的策略
        
        Args:
            strategy_name: 策略名称
            strategy_type: 策略类型 (entry/exit/filter)
            strategy_side: 策略方向 (long/short)
            strategy_code: 策略代码
            description: 策略描述
            author: 作者
            parameters: 策略参数
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 1. 验证策略代码
            if not self._validate_strategy_code(strategy_code, strategy_type):
                logger.error(f"策略代码验证失败: {strategy_name}")
                return False
            
            # 2. 生成策略文件
            file_path = self._generate_strategy_file(
                strategy_name, strategy_type, strategy_side, 
                strategy_code, description, author, parameters
            )
            
            # 3. 动态导入并注册策略
            if self._dynamic_import_strategy(file_path, strategy_name):
                # 4. 保存到数据库
                self._save_strategy_to_database(
                    strategy_name, strategy_type, strategy_side,
                    description, author, parameters, file_path
                )
                
                logger.info(f"成功注册LLM策略: {strategy_name}")
                return True
            else:
                logger.error(f"动态导入策略失败: {strategy_name}")
                return False
                
        except Exception as e:
            logger.error(f"注册LLM策略失败: {strategy_name}, 错误: {str(e)}")
            return False
    
    def _validate_strategy_code(self, code: str, strategy_type: str) -> bool:
        """验证策略代码的基本结构"""
        try:
            # 编译检查
            compile(code, '<string>', 'exec')
            
            # 检查必要的函数签名
            required_patterns = {
                'entry': ['def ', '_backtest(', 'df[\'entry_sig\']', 'df[\'entry_price\']'],
                'exit': ['def ', '_backtest(', 'df[\'sell_sig\']', 'df[\'sell_price\']'],
                'filter': ['def ', '_backtest(', 'df[\'entry_sig\']']
            }
            
            patterns = required_patterns.get(strategy_type, [])
            for pattern in patterns:
                if pattern not in code:
                    logger.warning(f"策略代码缺少必要模式: {pattern}")
            
            return True
            
        except SyntaxError as e:
            logger.error(f"策略代码语法错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"策略代码验证失败: {str(e)}")
            return False
    
    def _generate_strategy_file(self, name: str, type_: str, side: str, 
                              code: str, desc: str, author: str, params: Dict) -> str:
        """生成策略文件"""
        
        # 生成文件名
        filename = f"{name.lower().replace(' ', '_')}.py"
        file_path = os.path.join(self.auto_generated_dir, filename)
        
        # 生成完整的策略文件内容
        file_content = f'''#!/usr/bin/env python3
"""
自动生成的策略文件
策略名称: {name}
策略类型: {type_}
策略方向: {side}
描述: {desc}
作者: {author}
创建时间: {datetime.now().isoformat()}
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.data_object_center.st_instance import StrategyInstance

# 策略参数
STRATEGY_PARAMS = {json.dumps(params or {}, indent=4)}

@registry.register(name="{name}", desc="{desc}", side="{side}", type="{type_}")
def {name.lower().replace(' ', '_').replace('-', '_')}(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    """
    {desc}
    """
    if stIns is None:
        return {name.lower().replace(' ', '_').replace('-', '_')}_backtest(df)
    else:
        return {name.lower().replace(' ', '_').replace('-', '_')}_live(df, stIns)

def {name.lower().replace(' ', '_').replace('-', '_')}_backtest(df: pd.DataFrame) -> pd.DataFrame:
    """回测模式实现"""
{self._indent_code(code, 4)}

def {name.lower().replace(' ', '_').replace('-', '_')}_live(df: pd.DataFrame, stIns: StrategyInstance):
    """实盘模式实现（可选）"""
    # TODO: 实现实盘交易逻辑
    pass

if __name__ == '__main__':
    print(f"策略 {name} 已加载")
'''
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return file_path
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """为代码添加缩进"""
        indent = ' ' * spaces
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    def _dynamic_import_strategy(self, file_path: str, strategy_name: str) -> bool:
        """动态导入策略"""
        try:
            # 获取模块名
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            module_path = f"backend.strategy_center.atom_strategy.auto_generated.{module_name}"
            
            # 动态导入模块
            if module_path in sys.modules:
                # 重新加载模块
                importlib.reload(sys.modules[module_path])
            else:
                importlib.import_module(module_path)
            
            # 验证策略是否成功注册
            strategies = registry.list_strategies()
            for strategy in strategies:
                if strategy['name'] == strategy_name:
                    logger.info(f"策略 {strategy_name} 成功注册到registry")
                    return True
            
            logger.error(f"策略 {strategy_name} 未在registry中找到")
            return False
            
        except Exception as e:
            logger.error(f"动态导入策略失败: {str(e)}")
            return False
    
    def _save_strategy_to_database(self, name: str, type_: str, side: str,
                                 desc: str, author: str, params: Dict, file_path: str):
        """保存策略信息到数据库"""
        db_data = self._load_strategy_database()
        
        strategy_info = {
            "name": name,
            "type": type_,
            "side": side,
            "description": desc,
            "author": author,
            "parameters": params or {},
            "file_path": file_path,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        db_data["strategies"][name] = strategy_info
        self._save_strategy_database(db_data)
    
    def load_all_auto_generated_strategies(self):
        """加载所有自动生成的策略"""
        try:
            if not os.path.exists(self.auto_generated_dir):
                return
            
            for filename in os.listdir(self.auto_generated_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    try:
                        module_name = filename[:-3]  # 去掉.py后缀
                        module_path = f"backend.strategy_center.atom_strategy.auto_generated.{module_name}"
                        importlib.import_module(module_path)
                        logger.info(f"加载自动生成策略: {module_name}")
                    except Exception as e:
                        logger.error(f"加载策略文件失败 {filename}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"加载自动生成策略失败: {str(e)}")
    
    def get_strategy_database(self) -> Dict:
        """获取策略数据库"""
        return self._load_strategy_database()
    
    def delete_strategy(self, strategy_name: str) -> bool:
        """删除策略"""
        try:
            db_data = self._load_strategy_database()
            
            if strategy_name in db_data["strategies"]:
                strategy_info = db_data["strategies"][strategy_name]
                
                # 删除文件
                if os.path.exists(strategy_info["file_path"]):
                    os.remove(strategy_info["file_path"])
                
                # 从数据库中删除
                del db_data["strategies"][strategy_name]
                self._save_strategy_database(db_data)
                
                # 从registry中注销（如果可能）
                # 注意：Python中动态注销函数比较复杂，这里只是标记删除
                
                logger.info(f"成功删除策略: {strategy_name}")
                return True
            else:
                logger.warning(f"策略不存在: {strategy_name}")
                return False
                
        except Exception as e:
            logger.error(f"删除策略失败: {strategy_name}, 错误: {str(e)}")
            return False
    
    def update_strategy_status(self, strategy_name: str, status: str) -> bool:
        """更新策略状态"""
        try:
            db_data = self._load_strategy_database()
            
            if strategy_name in db_data["strategies"]:
                db_data["strategies"][strategy_name]["status"] = status
                db_data["strategies"][strategy_name]["updated_at"] = datetime.now().isoformat()
                self._save_strategy_database(db_data)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"更新策略状态失败: {str(e)}")
            return False


# 全局实例
dynamic_registry = DynamicStrategyRegistry()

# 启动时加载所有自动生成的策略
dynamic_registry.load_all_auto_generated_strategies() 