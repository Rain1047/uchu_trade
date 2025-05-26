#!/usr/bin/env python3
"""
AI增强规则提取器
使用对话形式深度分析文本，提取更精确的交易规则
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIRuleEnhancer:
    """AI增强规则提取器"""
    
    def __init__(self, extracted_text_dir: str, processed_rules_dir: str):
        self.extracted_text_dir = Path(extracted_text_dir)
        self.processed_rules_dir = Path(processed_rules_dir)
        self.processed_rules_dir.mkdir(exist_ok=True)
        
        # AI分析提示模板
        self.analysis_prompts = {
            'entry_rules': """
请仔细分析以下交易书籍文本，提取其中的入场规则。

需要提取的信息：
1. 规则名称：简洁明确的规则描述
2. 入场条件：具体的买入条件（技术指标、价格形态等）
3. 时间框架：短期（日内）、中期（几天到几周）、长期（几个月以上）
4. 技术指标：涉及的技术分析工具
5. 参数设置：具体的数值参数
6. 应用场景：市场环境、品种适用性

文本内容：
{text}

请以JSON格式输出，格式如下：
{{
  "entry_rules": [
    {{
      "name": "规则名称",
      "conditions": ["条件1", "条件2"],
      "timeframe": "short/medium/long",
      "indicators": ["指标1", "指标2"],
      "parameters": {{"param1": "value1"}},
      "market_context": "适用的市场环境",
      "confidence": 0.85
    }}
  ]
}}
""",
            
            'exit_rules': """
请仔细分析以下交易书籍文本，提取其中的出场规则（包括止盈和止损）。

需要提取的信息：
1. 规则名称：简洁明确的规则描述
2. 出场条件：具体的卖出条件
3. 止损设置：风险控制方法
4. 止盈设置：盈利目标设定
5. 时间框架：持仓时间预期
6. 风险收益比：预期的风险收益比例

文本内容：
{text}

请以JSON格式输出，格式如下：
{{
  "exit_rules": [
    {{
      "name": "规则名称",
      "exit_conditions": ["条件1", "条件2"],
      "stop_loss": "止损方法",
      "take_profit": "止盈方法",
      "risk_reward_ratio": "风险收益比",
      "timeframe": "short/medium/long",
      "confidence": 0.85
    }}
  ]
}}
""",
            
            'filter_rules': """
请仔细分析以下交易书籍文本，提取其中的过滤规则（筛选条件、风险控制等）。

需要提取的信息：
1. 过滤条件：筛选标准
2. 市场环境：适用的市场状态
3. 风险控制：风险管理方法
4. 仓位管理：资金分配规则
5. 时机选择：交易时机判断

文本内容：
{text}

请以JSON格式输出，格式如下：
{{
  "filter_rules": [
    {{
      "name": "规则名称",
      "filter_conditions": ["条件1", "条件2"],
      "market_environment": "市场环境要求",
      "risk_management": "风险管理方法",
      "position_sizing": "仓位管理规则",
      "confidence": 0.85
    }}
  ]
}}
"""
        }
    
    def analyze_text_with_ai_prompts(self, text_content: str, max_chunk_size: int = 3000) -> Dict[str, Any]:
        """
        使用AI提示分析文本
        这个方法展示了如何构建分析提示，实际使用时需要连接AI模型
        """
        # 将文本分块
        chunks = self._split_text_into_chunks(text_content, max_chunk_size)
        
        analysis_results = {
            'entry_rules': [],
            'exit_rules': [],
            'filter_rules': [],
            'summary': {}
        }
        
        for i, chunk in enumerate(chunks):
            logger.info(f"正在分析文本块 {i+1}/{len(chunks)}")
            
            # 分析入场规则
            entry_analysis = self._analyze_chunk_for_entries(chunk)
            analysis_results['entry_rules'].extend(entry_analysis)
            
            # 分析出场规则
            exit_analysis = self._analyze_chunk_for_exits(chunk)
            analysis_results['exit_rules'].extend(exit_analysis)
            
            # 分析过滤规则
            filter_analysis = self._analyze_chunk_for_filters(chunk)
            analysis_results['filter_rules'].extend(filter_analysis)
        
        # 生成汇总信息
        analysis_results['summary'] = self._generate_summary(analysis_results)
        
        return analysis_results
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """将文本分割成适合AI分析的块"""
        # 按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _analyze_chunk_for_entries(self, text_chunk: str) -> List[Dict[str, Any]]:
        """
        分析文本块中的入场规则
        这里是规则提取的模拟实现，实际使用时应该调用AI模型
        """
        entry_rules = []
        
        # 模拟规则提取逻辑
        entry_keywords = ['买入', '进场', '开仓', '入场', 'buy', 'entry', 'enter']
        condition_keywords = ['当', '如果', '突破', '跌破', '上穿', '下穿', 'when', 'if']
        
        for entry_kw in entry_keywords:
            if entry_kw in text_chunk.lower():
                # 查找相关条件
                conditions = []
                for condition_kw in condition_keywords:
                    if condition_kw in text_chunk.lower():
                        # 提取包含条件关键词的句子
                        sentences = text_chunk.split('。')
                        for sentence in sentences:
                            if condition_kw in sentence and entry_kw in sentence:
                                conditions.append(sentence.strip())
                
                if conditions:
                    rule = {
                        'name': f"入场规则_{len(entry_rules) + 1}",
                        'conditions': conditions[:3],  # 限制条件数量
                        'timeframe': self._detect_timeframe(text_chunk),
                        'indicators': self._extract_indicators(text_chunk),
                        'parameters': self._extract_parameters(text_chunk),
                        'market_context': self._detect_market_context(text_chunk),
                        'confidence': self._calculate_confidence(text_chunk, conditions)
                    }
                    entry_rules.append(rule)
        
        return entry_rules
    
    def _analyze_chunk_for_exits(self, text_chunk: str) -> List[Dict[str, Any]]:
        """分析文本块中的出场规则"""
        exit_rules = []
        
        exit_keywords = ['卖出', '出场', '平仓', '离场', 'sell', 'exit']
        stop_keywords = ['止损', 'stop loss', '止盈', 'take profit']
        
        for exit_kw in exit_keywords:
            if exit_kw in text_chunk.lower():
                conditions = []
                sentences = text_chunk.split('。')
                for sentence in sentences:
                    if exit_kw in sentence:
                        conditions.append(sentence.strip())
                
                if conditions:
                    rule = {
                        'name': f"出场规则_{len(exit_rules) + 1}",
                        'exit_conditions': conditions[:3],
                        'stop_loss': self._extract_stop_loss(text_chunk),
                        'take_profit': self._extract_take_profit(text_chunk),
                        'risk_reward_ratio': self._extract_risk_reward(text_chunk),
                        'timeframe': self._detect_timeframe(text_chunk),
                        'confidence': self._calculate_confidence(text_chunk, conditions)
                    }
                    exit_rules.append(rule)
        
        return exit_rules
    
    def _analyze_chunk_for_filters(self, text_chunk: str) -> List[Dict[str, Any]]:
        """分析文本块中的过滤规则"""
        filter_rules = []
        
        filter_keywords = ['筛选', '过滤', '选择', '避免', '风险', 'filter', 'screen']
        
        for filter_kw in filter_keywords:
            if filter_kw in text_chunk.lower():
                conditions = []
                sentences = text_chunk.split('。')
                for sentence in sentences:
                    if filter_kw in sentence:
                        conditions.append(sentence.strip())
                
                if conditions:
                    rule = {
                        'name': f"过滤规则_{len(filter_rules) + 1}",
                        'filter_conditions': conditions[:3],
                        'market_environment': self._detect_market_context(text_chunk),
                        'risk_management': self._extract_risk_management(text_chunk),
                        'position_sizing': self._extract_position_sizing(text_chunk),
                        'confidence': self._calculate_confidence(text_chunk, conditions)
                    }
                    filter_rules.append(rule)
        
        return filter_rules
    
    def _detect_timeframe(self, text: str) -> str:
        """检测时间框架"""
        timeframe_map = {
            'short': ['日内', '分钟', '小时', '短线', 'intraday', 'scalping'],
            'medium': ['日', '周', '中线', 'swing', 'days'],
            'long': ['月', '年', '长线', '投资', 'long-term', 'investment']
        }
        
        text_lower = text.lower()
        for timeframe, keywords in timeframe_map.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return timeframe
        
        return 'medium'  # 默认
    
    def _extract_indicators(self, text: str) -> List[str]:
        """提取技术指标"""
        indicators = []
        indicator_list = [
            'MA', 'EMA', 'SMA', 'MACD', 'RSI', 'KDJ', 'BOLL', 'CCI',
            'WR', 'BIAS', 'DMI', 'SAR', 'ATR', 'OBV', 'VOL',
            '移动平均线', '均线', '相对强弱指标', '布林带', '随机指标'
        ]
        
        for indicator in indicator_list:
            if indicator.upper() in text.upper():
                indicators.append(indicator)
        
        return list(set(indicators))
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """提取参数"""
        import re
        parameters = {}
        
        # 数值参数
        numbers = re.findall(r'(\d+(?:\.\d+)?)', text)
        if numbers:
            parameters['numeric_values'] = [float(n) for n in numbers[:5]]
        
        # 百分比
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        if percentages:
            parameters['percentages'] = [float(p) for p in percentages]
        
        return parameters
    
    def _detect_market_context(self, text: str) -> str:
        """检测市场环境"""
        market_contexts = {
            '牛市': ['上涨', '牛市', '看涨', 'bull', 'uptrend'],
            '熊市': ['下跌', '熊市', '看跌', 'bear', 'downtrend'],
            '震荡': ['震荡', '横盘', '整理', 'sideways', 'range']
        }
        
        text_lower = text.lower()
        for context, keywords in market_contexts.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return context
        
        return '通用'
    
    def _extract_stop_loss(self, text: str) -> str:
        """提取止损方法"""
        import re
        
        stop_patterns = [
            r'止损.*?(\d+(?:\.\d+)?%)',
            r'stop.*?loss.*?(\d+(?:\.\d+)?%)',
            r'损失.*?不超过.*?(\d+(?:\.\d+)?%)'
        ]
        
        for pattern in stop_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"止损{match.group(1)}"
        
        return "未明确"
    
    def _extract_take_profit(self, text: str) -> str:
        """提取止盈方法"""
        import re
        
        profit_patterns = [
            r'止盈.*?(\d+(?:\.\d+)?%)',
            r'take.*?profit.*?(\d+(?:\.\d+)?%)',
            r'盈利.*?目标.*?(\d+(?:\.\d+)?%)'
        ]
        
        for pattern in profit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"止盈{match.group(1)}"
        
        return "未明确"
    
    def _extract_risk_reward(self, text: str) -> str:
        """提取风险收益比"""
        import re
        
        ratio_patterns = [
            r'风险.*?收益.*?(\d+:\d+)',
            r'(\d+).*?倍.*?收益',
            r'risk.*?reward.*?(\d+:\d+)'
        ]
        
        for pattern in ratio_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "未明确"
    
    def _extract_risk_management(self, text: str) -> str:
        """提取风险管理方法"""
        risk_keywords = ['分散投资', '仓位控制', '风险分散', '止损', '资金管理']
        
        for keyword in risk_keywords:
            if keyword in text:
                return keyword
        
        return "未明确"
    
    def _extract_position_sizing(self, text: str) -> str:
        """提取仓位管理规则"""
        import re
        
        position_patterns = [
            r'仓位.*?(\d+(?:\.\d+)?%)',
            r'资金.*?(\d+(?:\.\d+)?%)',
            r'不超过.*?(\d+(?:\.\d+)?%)'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"仓位{match.group(1)}"
        
        return "未明确"
    
    def _calculate_confidence(self, text: str, conditions: List[str]) -> float:
        """计算置信度"""
        confidence = 0.5
        
        # 基于条件数量
        confidence += min(len(conditions) * 0.1, 0.3)
        
        # 基于文本长度
        if len(text) > 500:
            confidence += 0.1
        
        # 基于数值参数
        import re
        if re.search(r'\d+(?:\.\d+)?', text):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析汇总"""
        summary = {
            'total_entry_rules': len(analysis_results['entry_rules']),
            'total_exit_rules': len(analysis_results['exit_rules']),
            'total_filter_rules': len(analysis_results['filter_rules']),
            'timeframe_distribution': {},
            'indicator_usage': {},
            'average_confidence': 0.0
        }
        
        # 统计时间框架分布
        all_rules = (analysis_results['entry_rules'] + 
                    analysis_results['exit_rules'] + 
                    analysis_results['filter_rules'])
        
        confidences = []
        for rule in all_rules:
            timeframe = rule.get('timeframe', 'unknown')
            summary['timeframe_distribution'][timeframe] = (
                summary['timeframe_distribution'].get(timeframe, 0) + 1
            )
            
            confidence = rule.get('confidence', 0.5)
            confidences.append(confidence)
            
            # 统计指标使用
            indicators = rule.get('indicators', [])
            for indicator in indicators:
                summary['indicator_usage'][indicator] = (
                    summary['indicator_usage'].get(indicator, 0) + 1
                )
        
        if confidences:
            summary['average_confidence'] = sum(confidences) / len(confidences)
        
        return summary
    
    def process_text_file(self, text_filename: str) -> Dict[str, Any]:
        """处理单个文本文件"""
        text_path = self.extracted_text_dir / text_filename
        
        if not text_path.exists():
            logger.error(f"文本文件不存在: {text_path}")
            return {}
        
        logger.info(f"开始AI分析: {text_filename}")
        
        # 读取文本
        with open(text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # AI分析
        analysis_results = self.analyze_text_with_ai_prompts(text_content)
        
        # 保存结果
        output_filename = f"{text_path.stem}_ai_analysis.json"
        output_path = self.processed_rules_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"AI分析完成: {text_filename}")
        return analysis_results
    
    def generate_conversation_prompts(self, text_chunk: str) -> Dict[str, str]:
        """
        生成用于对话式分析的提示
        这些提示可以在对话中逐步使用
        """
        prompts = {
            'initial_analysis': f"""
我有一段交易书籍的文本，想要提取其中的交易规则。请帮我分析这段文本：

```
{text_chunk[:1000]}...
```

请先告诉我这段文本主要讨论的是什么交易策略或方法？
""",
            
            'detailed_rules': """
很好！现在请帮我从这段文本中提取具体的交易规则，包括：

1. 入场条件：什么时候买入？
2. 出场条件：什么时候卖出？
3. 风险控制：如何设置止损？
4. 资金管理：如何控制仓位？

请尽可能详细和具体。
""",
            
            'parameters': """
现在请帮我识别这些规则中的具体参数，比如：
- 技术指标的周期设置
- 止损止盈的百分比
- 仓位大小的限制
- 时间框架的选择

这些参数对于实际应用很重要。
""",
            
            'implementation': """
最后，请帮我把这些规则整理成可以程序化实现的格式，包括：
- 明确的条件判断逻辑
- 具体的数值参数
- 优先级和执行顺序
- 特殊情况的处理

格式要求是结构化的JSON。
"""
        }
        
        return prompts

if __name__ == "__main__":
    # 设置路径
    current_dir = Path(__file__).parent
    extracted_text_dir = current_dir.parent / "extracted_text"
    processed_rules_dir = current_dir.parent / "processed_rules"
    
    # 创建AI增强器
    enhancer = AIRuleEnhancer(str(extracted_text_dir), str(processed_rules_dir))
    
    # 示例：处理文本文件
    text_files = list(extracted_text_dir.glob('*.txt'))
    if text_files:
        sample_file = text_files[0]
        print(f"正在分析示例文件: {sample_file.name}")
        
        # 生成对话提示
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_text = f.read()[:2000]  # 取前2000字符作为示例
        
        prompts = enhancer.generate_conversation_prompts(sample_text)
        
        print("\n=== 对话式分析提示 ===")
        for stage, prompt in prompts.items():
            print(f"\n{stage.upper()}:")
            print(prompt)
            print("-" * 50) 