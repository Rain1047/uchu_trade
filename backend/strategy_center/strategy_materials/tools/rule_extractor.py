#!/usr/bin/env python3
"""
交易规则提取器
使用AI分析交易书籍文本，提取结构化的交易规则
"""

import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingRule:
    """交易规则数据结构"""
    rule_id: str
    name: str
    type: str  # entry, exit, filter
    timeframe: str  # long, medium, short
    conditions: List[str]
    signals: List[str]
    parameters: Dict[str, Any]
    source: str
    confidence: float
    description: str
    chapter: str = ""
    page_reference: str = ""

class RuleExtractor:
    """交易规则提取器"""
    
    def __init__(self, extracted_text_dir: str, processed_rules_dir: str):
        self.extracted_text_dir = Path(extracted_text_dir)
        self.processed_rules_dir = Path(processed_rules_dir)
        self.processed_rules_dir.mkdir(exist_ok=True)
        
        # 规则提取模式
        self.rule_patterns = {
            'entry_signals': [
                r'买入.*?当.*?',
                r'入场.*?条件.*?',
                r'开仓.*?信号.*?',
                r'进场.*?时机.*?',
                r'entry.*?signal.*?',
                r'buy.*?when.*?',
                r'如果.*?则买入',
                r'当.*?时买入',
            ],
            'exit_signals': [
                r'卖出.*?当.*?',
                r'出场.*?条件.*?',
                r'平仓.*?信号.*?',
                r'离场.*?时机.*?',
                r'exit.*?signal.*?',
                r'sell.*?when.*?',
                r'如果.*?则卖出',
                r'当.*?时卖出',
            ],
            'stop_loss': [
                r'止损.*?',
                r'stop.*?loss.*?',
                r'风险控制.*?',
                r'最大损失.*?',
                r'止损价.*?',
            ],
            'take_profit': [
                r'止盈.*?',
                r'take.*?profit.*?',
                r'获利了结.*?',
                r'目标价.*?',
                r'盈利目标.*?',
            ]
        }
        
        # 技术指标识别
        self.technical_indicators = [
            'MA', 'EMA', 'SMA', 'MACD', 'RSI', 'KDJ', 'BOLL', 'CCI',
            'WR', 'BIAS', 'DMI', 'SAR', 'ATR', 'OBV', 'VOL',
            '移动平均线', '均线', '相对强弱指标', '布林带', '随机指标'
        ]
        
        # 时间框架识别
        self.timeframe_keywords = {
            'short': ['日内', '短线', '分钟', '小时', '当日', '日内交易', 'intraday', 'scalping'],
            'medium': ['中线', '周线', '几天', '数周', 'swing', 'medium-term'],
            'long': ['长线', '月线', '长期', '投资', '价值', 'long-term', 'investment']
        }
    
    def extract_text_chunks(self, text: str, chunk_size: int = 2000) -> List[str]:
        """将长文本分割成块以便处理"""
        chunks = []
        lines = text.split('\n')
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) < chunk_size:
                current_chunk += line + "\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def identify_timeframe(self, text: str) -> str:
        """识别交易时间框架"""
        text_lower = text.lower()
        
        for timeframe, keywords in self.timeframe_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return timeframe
        
        return 'medium'  # 默认中期
    
    def extract_technical_indicators(self, text: str) -> List[str]:
        """提取技术指标"""
        indicators = []
        for indicator in self.technical_indicators:
            if indicator.upper() in text.upper():
                indicators.append(indicator)
        return list(set(indicators))
    
    def extract_rules_from_chunk(self, text_chunk: str, source: str) -> List[TradingRule]:
        """从文本块中提取交易规则"""
        rules = []
        
        # 识别时间框架
        timeframe = self.identify_timeframe(text_chunk)
        
        # 提取技术指标
        indicators = self.extract_technical_indicators(text_chunk)
        
        # 使用模式匹配提取规则
        for rule_type, patterns in self.rule_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_chunk, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    rule_text = match.group(0)
                    
                    # 扩展匹配的上下文
                    start = max(0, match.start() - 200)
                    end = min(len(text_chunk), match.end() + 200)
                    context = text_chunk[start:end]
                    
                    rule = self._create_rule_from_text(
                        rule_text, context, rule_type, timeframe, indicators, source
                    )
                    if rule:
                        rules.append(rule)
        
        return rules
    
    def _create_rule_from_text(self, rule_text: str, context: str, rule_type: str, 
                              timeframe: str, indicators: List[str], source: str) -> Optional[TradingRule]:
        """从文本创建交易规则对象"""
        try:
            # 生成唯一ID
            rule_id = str(uuid.uuid4())[:8]
            
            # 提取规则名称
            name = self._extract_rule_name(rule_text)
            
            # 提取条件和信号
            conditions = self._extract_conditions(context)
            signals = self._extract_signals(context)
            
            # 提取参数
            parameters = self._extract_parameters(context, indicators)
            
            # 计算置信度
            confidence = self._calculate_confidence(rule_text, context, indicators)
            
            # 确定规则类型
            if rule_type in ['entry_signals']:
                rule_category = 'entry'
            elif rule_type in ['exit_signals']:
                rule_category = 'exit'
            elif rule_type in ['stop_loss', 'take_profit']:
                rule_category = 'exit'
            else:
                rule_category = 'filter'
            
            rule = TradingRule(
                rule_id=rule_id,
                name=name,
                type=rule_category,
                timeframe=timeframe,
                conditions=conditions,
                signals=signals,
                parameters=parameters,
                source=source,
                confidence=confidence,
                description=rule_text[:200] + "..." if len(rule_text) > 200 else rule_text
            )
            
            return rule
            
        except Exception as e:
            logger.warning(f"创建规则失败: {e}")
            return None
    
    def _extract_rule_name(self, text: str) -> str:
        """提取规则名称"""
        # 简单的名称提取逻辑
        text = text.strip()
        if len(text) > 50:
            return text[:50] + "..."
        return text
    
    def _extract_conditions(self, text: str) -> List[str]:
        """提取交易条件"""
        conditions = []
        
        # 数值条件模式
        number_patterns = [
            r'大于\s*(\d+(?:\.\d+)?)',
            r'小于\s*(\d+(?:\.\d+)?)',
            r'超过\s*(\d+(?:\.\d+)?)',
            r'低于\s*(\d+(?:\.\d+)?)',
            r'>\s*(\d+(?:\.\d+)?)',
            r'<\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in number_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                conditions.append(match.group(0))
        
        # 趋势条件
        trend_patterns = [
            r'上涨.*?', r'下跌.*?', r'突破.*?', r'跌破.*?',
            r'上穿.*?', r'下穿.*?', r'金叉.*?', r'死叉.*?'
        ]
        
        for pattern in trend_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conditions.append(match.group(0))
        
        return conditions[:5]  # 限制条件数量
    
    def _extract_signals(self, text: str) -> List[str]:
        """提取交易信号"""
        signals = []
        
        signal_patterns = [
            r'信号.*?', r'指标.*?', r'形态.*?', r'pattern.*?'
        ]
        
        for pattern in signal_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                signals.append(match.group(0))
        
        return signals[:3]  # 限制信号数量
    
    def _extract_parameters(self, text: str, indicators: List[str]) -> Dict[str, Any]:
        """提取参数"""
        parameters = {}
        
        # 周期参数
        period_pattern = r'(\d+)\s*(?:日|天|周|月|分钟|小时|period|day)'
        matches = re.finditer(period_pattern, text)
        for match in matches:
            parameters['period'] = int(match.group(1))
        
        # 指标参数
        for indicator in indicators:
            parameters[f'{indicator}_used'] = True
        
        # 百分比参数
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        matches = re.finditer(percent_pattern, text)
        for match in matches:
            parameters['threshold_percent'] = float(match.group(1))
        
        return parameters
    
    def _calculate_confidence(self, rule_text: str, context: str, indicators: List[str]) -> float:
        """计算规则置信度"""
        confidence = 0.5  # 基础置信度
        
        # 有具体数值的规则置信度更高
        if re.search(r'\d+(?:\.\d+)?', rule_text):
            confidence += 0.2
        
        # 有技术指标的规则置信度更高
        if indicators:
            confidence += 0.1 * len(indicators)
        
        # 上下文长度影响置信度
        if len(context) > 500:
            confidence += 0.1
        
        # 有明确关键词的规则置信度更高
        key_phrases = ['如果', '当', '则', 'if', 'when', 'then']
        for phrase in key_phrases:
            if phrase in rule_text.lower():
                confidence += 0.05
        
        return min(confidence, 1.0)
    
    def process_text_file(self, text_filename: str) -> List[TradingRule]:
        """处理单个文本文件，提取交易规则"""
        text_path = self.extracted_text_dir / text_filename
        
        if not text_path.exists():
            logger.error(f"文本文件不存在: {text_path}")
            return []
        
        logger.info(f"开始提取规则: {text_filename}")
        
        # 读取文本
        with open(text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # 分割文本
        chunks = self.extract_text_chunks(text_content)
        
        # 提取规则
        all_rules = []
        for i, chunk in enumerate(chunks):
            rules = self.extract_rules_from_chunk(chunk, text_filename)
            all_rules.extend(rules)
            logger.info(f"块 {i+1}/{len(chunks)}: 提取到 {len(rules)} 条规则")
        
        # 去重和过滤
        filtered_rules = self._filter_and_deduplicate_rules(all_rules)
        
        # 保存规则
        rules_filename = f"{text_path.stem}_rules.json"
        self._save_rules(filtered_rules, rules_filename)
        
        logger.info(f"完成处理: {text_filename}, 提取到 {len(filtered_rules)} 条有效规则")
        return filtered_rules
    
    def _filter_and_deduplicate_rules(self, rules: List[TradingRule]) -> List[TradingRule]:
        """过滤和去重规则"""
        # 按置信度排序
        rules.sort(key=lambda x: x.confidence, reverse=True)
        
        # 去重（基于描述的相似性）
        unique_rules = []
        seen_descriptions = set()
        
        for rule in rules:
            # 简单的去重逻辑
            desc_key = rule.description[:50].lower().strip()
            if desc_key not in seen_descriptions and rule.confidence > 0.3:
                unique_rules.append(rule)
                seen_descriptions.add(desc_key)
        
        return unique_rules[:20]  # 限制每个文件最多20条规则
    
    def _save_rules(self, rules: List[TradingRule], filename: str):
        """保存规则到JSON文件"""
        rules_data = [asdict(rule) for rule in rules]
        
        output_path = self.processed_rules_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"规则已保存到: {output_path}")
    
    def process_all_text_files(self) -> Dict[str, Any]:
        """处理所有文本文件"""
        results = {
            'processed_files': [],
            'total_rules': 0,
            'rules_by_type': {},
            'rules_by_timeframe': {},
        }
        
        text_files = list(self.extracted_text_dir.glob('*.txt'))
        
        for text_file in text_files:
            rules = self.process_text_file(text_file.name)
            
            file_result = {
                'filename': text_file.name,
                'rule_count': len(rules),
                'rules': [asdict(rule) for rule in rules]
            }
            results['processed_files'].append(file_result)
            results['total_rules'] += len(rules)
            
            # 统计规则类型和时间框架
            for rule in rules:
                rule_type = rule.type
                timeframe = rule.timeframe
                
                results['rules_by_type'][rule_type] = results['rules_by_type'].get(rule_type, 0) + 1
                results['rules_by_timeframe'][timeframe] = results['rules_by_timeframe'].get(timeframe, 0) + 1
        
        # 保存汇总结果
        summary_path = self.processed_rules_dir / "extraction_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"规则提取完成: 总计 {results['total_rules']} 条规则")
        return results

if __name__ == "__main__":
    # 设置路径
    current_dir = Path(__file__).parent
    extracted_text_dir = current_dir.parent / "extracted_text"
    processed_rules_dir = current_dir.parent / "processed_rules"
    
    # 创建提取器并运行
    extractor = RuleExtractor(str(extracted_text_dir), str(processed_rules_dir))
    results = extractor.process_all_text_files()
    
    print(f"\n规则提取结果:")
    print(f"处理文件数: {len(results['processed_files'])}")
    print(f"总规则数: {results['total_rules']}")
    print(f"按类型分布: {results['rules_by_type']}")
    print(f"按时间框架分布: {results['rules_by_timeframe']}") 