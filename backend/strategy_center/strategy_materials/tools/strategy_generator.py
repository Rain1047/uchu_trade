#!/usr/bin/env python3
"""
策略生成器
将提取的交易规则转换为可执行的策略代码
"""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StrategyTemplate:
    """策略模板"""
    name: str
    timeframe: str
    entry_rules: List[Dict[str, Any]]
    exit_rules: List[Dict[str, Any]]
    filter_rules: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    source_book: str

class StrategyGenerator:
    """策略生成器"""
    
    def __init__(self, processed_rules_dir: str, final_strategies_dir: str):
        self.processed_rules_dir = Path(processed_rules_dir)
        self.final_strategies_dir = Path(final_strategies_dir)
        self.final_strategies_dir.mkdir(exist_ok=True)
        
        # 策略代码模板
        self.strategy_templates = {
            'base_template': '''
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class {strategy_class_name}:
    """
    {strategy_description}
    
    来源: {source_book}
    时间框架: {timeframe}
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.name = "{strategy_name}"
        self.timeframe = "{timeframe}"
        self.parameters = parameters or {default_parameters}
        
        # 策略状态
        self.position = 0  # 0: 空仓, 1: 多头, -1: 空头
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
        
    def check_entry_conditions(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """检查入场条件"""
        if current_index < 50:  # 确保有足够的历史数据
            return {{"signal": "no_action", "reason": "insufficient_data"}}
        
        current_row = df.iloc[current_index]
        
        # 入场条件检查
{entry_conditions_code}
        
        return {{"signal": "no_action", "reason": "conditions_not_met"}}
    
    def check_exit_conditions(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """检查出场条件"""
        if self.position == 0:
            return {{"signal": "no_action", "reason": "no_position"}}
        
        current_row = df.iloc[current_index]
        current_price = current_row['close']
        
        # 止损检查
        if self.stop_loss_price and current_price <= self.stop_loss_price:
            return {{"signal": "exit", "reason": "stop_loss", "price": current_price}}
        
        # 止盈检查
        if self.take_profit_price and current_price >= self.take_profit_price:
            return {{"signal": "exit", "reason": "take_profit", "price": current_price}}
        
        # 其他出场条件
{exit_conditions_code}
        
        return {{"signal": "no_action", "reason": "hold_position"}}
    
    def calculate_position_size(self, account_balance: float, risk_percent: float = 2.0) -> float:
        """计算仓位大小"""
        risk_amount = account_balance * (risk_percent / 100)
        if self.entry_price and self.stop_loss_price:
            risk_per_share = abs(self.entry_price - self.stop_loss_price)
            if risk_per_share > 0:
                return risk_amount / risk_per_share
        return account_balance * 0.1  # 默认10%仓位
    
    def execute_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行策略"""
        signals = []
        
        for i in range(len(df)):
            if self.position == 0:
                # 检查入场条件
                entry_signal = self.check_entry_conditions(df, i)
                if entry_signal["signal"] == "buy":
                    self.position = 1
                    self.entry_price = entry_signal["price"]
                    self.stop_loss_price = entry_signal.get("stop_loss")
                    self.take_profit_price = entry_signal.get("take_profit")
                    signals.append({{"index": i, "signal": "buy", "price": self.entry_price}})
                elif entry_signal["signal"] == "sell":
                    self.position = -1
                    self.entry_price = entry_signal["price"]
                    self.stop_loss_price = entry_signal.get("stop_loss")
                    self.take_profit_price = entry_signal.get("take_profit")
                    signals.append({{"index": i, "signal": "sell", "price": self.entry_price}})
            else:
                # 检查出场条件
                exit_signal = self.check_exit_conditions(df, i)
                if exit_signal["signal"] == "exit":
                    signals.append({{"index": i, "signal": "exit", "price": exit_signal["price"]}})
                    self.position = 0
                    self.entry_price = None
                    self.stop_loss_price = None
                    self.take_profit_price = None
        
        # 将信号添加到DataFrame
        df_copy = df.copy()
        df_copy['signal'] = 'hold'
        df_copy['signal_price'] = np.nan
        
        for signal in signals:
            df_copy.loc[signal["index"], 'signal'] = signal["signal"]
            df_copy.loc[signal["index"], 'signal_price'] = signal["price"]
        
        return df_copy
''',
            
            'condition_template': '''
        # {condition_name}
        if {condition_logic}:
            # 设置止损和止盈
            stop_loss = current_price * {stop_loss_percent}
            take_profit = current_price * {take_profit_percent}
            
            return {{
                "signal": "{signal_type}",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "{condition_name}"
            }}
'''
        }
    
    def load_processed_rules(self, filename: str) -> Dict[str, Any]:
        """加载处理过的规则"""
        file_path = self.processed_rules_dir / filename
        
        if not file_path.exists():
            logger.error(f"规则文件不存在: {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_condition_code(self, rules: List[Dict[str, Any]], rule_type: str) -> str:
        """生成条件检查代码"""
        condition_codes = []
        
        for i, rule in enumerate(rules):
            if rule.get('confidence', 0) < 0.5:  # 跳过低置信度规则
                continue
            
            condition_name = rule.get('name', f'{rule_type}_condition_{i}')
            conditions = rule.get('conditions', [])
            
            if not conditions:
                continue
            
            # 生成条件逻辑
            condition_logic = self._convert_conditions_to_code(conditions)
            
            if condition_logic:
                # 确定信号类型
                signal_type = 'buy' if rule_type == 'entry' else 'exit'
                
                # 设置止损止盈参数
                stop_loss_percent = self._extract_stop_loss_percent(rule)
                take_profit_percent = self._extract_take_profit_percent(rule)
                
                condition_code = self.strategy_templates['condition_template'].format(
                    condition_name=condition_name,
                    condition_logic=condition_logic,
                    signal_type=signal_type,
                    stop_loss_percent=stop_loss_percent,
                    take_profit_percent=take_profit_percent
                )
                condition_codes.append(condition_code)
        
        return '\n'.join(condition_codes)
    
    def _convert_conditions_to_code(self, conditions: List[str]) -> str:
        """将文本条件转换为代码逻辑"""
        code_conditions = []
        
        for condition in conditions:
            # 简单的条件转换逻辑
            if '突破' in condition:
                code_conditions.append("current_price > df.iloc[current_index-1]['high']")
            elif '跌破' in condition:
                code_conditions.append("current_price < df.iloc[current_index-1]['low']")
            elif '上穿' in condition:
                code_conditions.append("current_price > current_row['ma20']")
            elif '下穿' in condition:
                code_conditions.append("current_price < current_row['ma20']")
            elif 'RSI' in condition:
                if '大于' in condition or '>' in condition:
                    code_conditions.append("current_row.get('rsi', 50) > 70")
                elif '小于' in condition or '<' in condition:
                    code_conditions.append("current_row.get('rsi', 50) < 30")
            elif 'MACD' in condition:
                if '金叉' in condition:
                    code_conditions.append("current_row.get('macd', 0) > current_row.get('macd_signal', 0)")
                elif '死叉' in condition:
                    code_conditions.append("current_row.get('macd', 0) < current_row.get('macd_signal', 0)")
        
        if code_conditions:
            return ' and '.join(code_conditions)
        else:
            return "False"  # 默认条件不满足
    
    def _extract_stop_loss_percent(self, rule: Dict[str, Any]) -> float:
        """提取止损百分比"""
        stop_loss = rule.get('stop_loss', '')
        if '%' in stop_loss:
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', stop_loss)
            if match:
                return 1 - float(match.group(1)) / 100
        return 0.95  # 默认5%止损
    
    def _extract_take_profit_percent(self, rule: Dict[str, Any]) -> float:
        """提取止盈百分比"""
        take_profit = rule.get('take_profit', '')
        if '%' in take_profit:
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', take_profit)
            if match:
                return 1 + float(match.group(1)) / 100
        return 1.10  # 默认10%止盈
    
    def generate_strategy_code(self, rules_data: Dict[str, Any], strategy_name: str, source_book: str) -> str:
        """生成完整的策略代码"""
        # 提取规则
        entry_rules = rules_data.get('entry_rules', [])
        exit_rules = rules_data.get('exit_rules', [])
        filter_rules = rules_data.get('filter_rules', [])
        
        # 确定时间框架
        timeframe = self._determine_timeframe(entry_rules + exit_rules)
        
        # 生成条件代码
        entry_conditions_code = self.generate_condition_code(entry_rules, 'entry')
        exit_conditions_code = self.generate_condition_code(exit_rules, 'exit')
        
        # 生成默认参数
        default_parameters = self._generate_default_parameters(entry_rules + exit_rules)
        
        # 生成策略类名
        strategy_class_name = ''.join(word.capitalize() for word in strategy_name.split('_'))
        
        # 填充模板
        strategy_code = self.strategy_templates['base_template'].format(
            strategy_class_name=strategy_class_name,
            strategy_name=strategy_name,
            strategy_description=f"基于《{source_book}》提取的交易策略",
            source_book=source_book,
            timeframe=timeframe,
            default_parameters=json.dumps(default_parameters, ensure_ascii=False, indent=8),
            entry_conditions_code=entry_conditions_code,
            exit_conditions_code=exit_conditions_code
        )
        
        return strategy_code
    
    def _determine_timeframe(self, rules: List[Dict[str, Any]]) -> str:
        """确定策略时间框架"""
        timeframes = [rule.get('timeframe', 'medium') for rule in rules]
        
        # 统计最常见的时间框架
        timeframe_counts = {}
        for tf in timeframes:
            timeframe_counts[tf] = timeframe_counts.get(tf, 0) + 1
        
        if timeframe_counts:
            return max(timeframe_counts, key=timeframe_counts.get)
        return 'medium'
    
    def _generate_default_parameters(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成默认参数"""
        parameters = {
            'risk_percent': 2.0,
            'max_position_size': 0.2,
            'stop_loss_percent': 5.0,
            'take_profit_percent': 10.0
        }
        
        # 从规则中提取参数
        for rule in rules:
            rule_params = rule.get('parameters', {})
            for key, value in rule_params.items():
                if key not in parameters:
                    parameters[key] = value
        
        return parameters
    
    def create_strategy_config(self, strategy_name: str, rules_data: Dict[str, Any], source_book: str) -> Dict[str, Any]:
        """创建策略配置文件"""
        config = {
            'strategy_id': str(uuid.uuid4())[:8],
            'name': strategy_name,
            'source_book': source_book,
            'timeframe': self._determine_timeframe(rules_data.get('entry_rules', []) + rules_data.get('exit_rules', [])),
            'description': f"基于《{source_book}》提取的交易策略",
            'rule_counts': {
                'entry_rules': len(rules_data.get('entry_rules', [])),
                'exit_rules': len(rules_data.get('exit_rules', [])),
                'filter_rules': len(rules_data.get('filter_rules', []))
            },
            'parameters': self._generate_default_parameters(
                rules_data.get('entry_rules', []) + rules_data.get('exit_rules', [])
            ),
            'risk_management': {
                'max_drawdown': 20.0,
                'position_sizing': 'fixed_percentage',
                'stop_loss_type': 'percentage',
                'take_profit_type': 'percentage'
            },
            'created_at': pd.Timestamp.now().isoformat(),
            'confidence_score': self._calculate_overall_confidence(rules_data)
        }
        
        return config
    
    def _calculate_overall_confidence(self, rules_data: Dict[str, Any]) -> float:
        """计算整体置信度"""
        all_rules = (
            rules_data.get('entry_rules', []) +
            rules_data.get('exit_rules', []) +
            rules_data.get('filter_rules', [])
        )
        
        if not all_rules:
            return 0.0
        
        confidences = [rule.get('confidence', 0.5) for rule in all_rules]
        return sum(confidences) / len(confidences)
    
    def process_rules_file(self, rules_filename: str) -> Optional[str]:
        """处理规则文件，生成策略"""
        # 加载规则
        rules_data = self.load_processed_rules(rules_filename)
        if not rules_data:
            return None
        
        # 生成策略名称
        base_name = rules_filename.replace('_rules.json', '').replace('_ai_analysis.json', '')
        strategy_name = f"strategy_{base_name}"
        
        # 确定来源书籍
        source_book = base_name.replace('_', ' ')
        
        logger.info(f"开始生成策略: {strategy_name}")
        
        # 生成策略代码
        strategy_code = self.generate_strategy_code(rules_data, strategy_name, source_book)
        
        # 生成策略配置
        strategy_config = self.create_strategy_config(strategy_name, rules_data, source_book)
        
        # 保存策略代码
        code_filename = f"{strategy_name}.py"
        code_path = self.final_strategies_dir / code_filename
        
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(strategy_code)
        
        # 保存策略配置
        config_filename = f"{strategy_name}_config.json"
        config_path = self.final_strategies_dir / config_filename
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(strategy_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"策略生成完成: {strategy_name}")
        return strategy_name
    
    def process_all_rules(self) -> Dict[str, Any]:
        """处理所有规则文件，生成策略"""
        results = {
            'generated_strategies': [],
            'failed_files': [],
            'total_files': 0,
            'success_count': 0
        }
        
        # 查找所有规则文件
        rule_files = list(self.processed_rules_dir.glob('*_rules.json'))
        rule_files.extend(list(self.processed_rules_dir.glob('*_ai_analysis.json')))
        
        results['total_files'] = len(rule_files)
        
        for rule_file in rule_files:
            try:
                strategy_name = self.process_rules_file(rule_file.name)
                if strategy_name:
                    results['generated_strategies'].append(strategy_name)
                    results['success_count'] += 1
                else:
                    results['failed_files'].append(rule_file.name)
            except Exception as e:
                logger.error(f"处理文件失败 {rule_file.name}: {e}")
                results['failed_files'].append(rule_file.name)
        
        # 保存生成汇总
        summary_path = self.final_strategies_dir / "generation_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"策略生成完成: {results['success_count']}/{results['total_files']} 成功")
        return results

if __name__ == "__main__":
    import pandas as pd
    
    # 设置路径
    current_dir = Path(__file__).parent
    processed_rules_dir = current_dir.parent / "processed_rules"
    final_strategies_dir = current_dir.parent / "final_strategies"
    
    # 创建策略生成器
    generator = StrategyGenerator(str(processed_rules_dir), str(final_strategies_dir))
    
    # 处理所有规则文件
    results = generator.process_all_rules()
    
    print(f"\n策略生成结果:")
    print(f"处理文件数: {results['total_files']}")
    print(f"成功生成: {results['success_count']}")
    print(f"生成的策略: {results['generated_strategies']}")
    
    if results['failed_files']:
        print(f"失败的文件: {results['failed_files']}") 