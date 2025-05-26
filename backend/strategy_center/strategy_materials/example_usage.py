#!/usr/bin/env python3
"""
交易规则提取系统使用示例
演示如何在对话中使用这个系统来提取交易规则
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "tools"))

from tools.ai_rule_enhancer import AIRuleEnhancer

def demo_conversation_analysis():
    """演示对话式分析"""
    
    # 示例交易文本
    sample_text = """
    海龟交易法则是一个完整的趋势跟踪系统。其核心原理如下：

    入场规则：
    1. 当价格突破20日最高价时，买入做多
    2. 当价格跌破20日最低价时，卖出做空
    3. 必须确认突破有效，即收盘价确实超过了前20日的最高价

    出场规则：
    1. 当价格跌破10日最低价时，平掉多头仓位
    2. 当价格突破10日最高价时，平掉空头仓位
    3. 止损设置在入场价格的2个ATR距离

    仓位管理：
    1. 每次交易的风险不超过账户资金的2%
    2. 根据ATR计算具体的仓位大小
    3. 最大仓位不超过账户资金的20%

    市场选择：
    1. 选择流动性好的市场
    2. 避免在震荡市中使用
    3. 适合中长期趋势明显的品种
    """
    
    print("=== 交易规则提取系统对话示例 ===\n")
    
    # 创建AI增强器
    enhancer = AIRuleEnhancer("extracted_text", "processed_rules")
    
    # 生成对话提示
    prompts = enhancer.generate_conversation_prompts(sample_text)
    
    print("📝 第一步：初步分析")
    print("=" * 50)
    print(prompts['initial_analysis'])
    print("\n" + "=" * 50)
    
    print("\n🔍 第二步：详细规则提取")
    print("=" * 50)
    print(prompts['detailed_rules'])
    print("\n" + "=" * 50)
    
    print("\n⚙️ 第三步：参数识别")
    print("=" * 50)
    print(prompts['parameters'])
    print("\n" + "=" * 50)
    
    print("\n💻 第四步：代码实现")
    print("=" * 50)
    print(prompts['implementation'])
    print("\n" + "=" * 50)
    
    print("\n✨ 对话式分析的优势：")
    print("1. 逐步深入，确保理解准确")
    print("2. 可以实时调整和优化")
    print("3. 支持多轮验证和细化")
    print("4. 最终生成可执行的代码")

def demo_rule_analysis():
    """演示规则分析过程"""
    
    print("\n=== 规则分析演示 ===\n")
    
    # 示例文本
    text_chunk = """
    当RSI指标超过70时，表明市场可能过热，此时应该考虑卖出。
    但是，在强势上涨趋势中，RSI可能会在高位停留较长时间。
    因此，最好结合其他指标，如MACD的背离信号来确认卖出时机。
    """
    
    enhancer = AIRuleEnhancer("extracted_text", "processed_rules")
    
    # 分析入场规则
    entry_rules = enhancer._analyze_chunk_for_entries(text_chunk)
    print("📈 提取的入场规则:")
    for i, rule in enumerate(entry_rules, 1):
        print(f"  {i}. {rule['name']}")
        print(f"     条件: {rule['conditions']}")
        print(f"     置信度: {rule['confidence']:.2f}")
        print()
    
    # 分析出场规则
    exit_rules = enhancer._analyze_chunk_for_exits(text_chunk)
    print("📉 提取的出场规则:")
    for i, rule in enumerate(exit_rules, 1):
        print(f"  {i}. {rule['name']}")
        print(f"     条件: {rule['exit_conditions']}")
        print(f"     置信度: {rule['confidence']:.2f}")
        print()
    
    # 检测技术指标
    indicators = enhancer._extract_indicators(text_chunk)
    print(f"🔧 检测到的技术指标: {indicators}")
    
    # 检测时间框架
    timeframe = enhancer._detect_timeframe(text_chunk)
    print(f"⏰ 检测到的时间框架: {timeframe}")

def demo_conversation_scenarios():
    """演示不同的对话场景"""
    
    print("\n=== 对话场景演示 ===\n")
    
    scenarios = [
        {
            "title": "场景1：分析具体策略",
            "user_input": """
我想分析这段关于均线策略的文本：

"当5日均线上穿20日均线时买入，当5日均线下穿20日均线时卖出。
同时要求成交量比前一日放大50%以上，确保突破的有效性。
止损设置为买入价的3%，止盈目标为买入价的10%。"

请帮我提取其中的交易规则。
""",
            "ai_response": """
基于你提供的文本，我提取到以下交易规则：

**入场规则：**
- 技术条件：5日均线上穿20日均线
- 成交量确认：成交量比前一日放大50%以上
- 时间框架：短期到中期

**出场规则：**
- 正常出场：5日均线下穿20日均线
- 止损：买入价下跌3%
- 止盈：买入价上涨10%

**参数设置：**
- 均线周期：5日、20日
- 成交量倍数：1.5倍
- 止损比例：3%
- 止盈比例：10%

这是一个典型的均线交叉策略，结合了成交量确认和明确的风险控制。
"""
        },
        
        {
            "title": "场景2：优化现有规则",
            "user_input": """
我之前提取了一个RSI策略：RSI > 80时卖出。
但在实际使用中发现，强势股的RSI经常长时间停留在高位。
请帮我优化这个规则。
""",
            "ai_response": """
你遇到的问题很常见。RSI在强势趋势中确实会出现"钝化"现象。建议优化如下：

**优化方案1：动态阈值**
- 在上升趋势中，将RSI阈值提高到85-90
- 结合趋势判断（如价格在20日均线之上）

**优化方案2：多重确认**
- RSI > 80 + MACD背离 + 成交量萎缩
- 三个条件同时满足才卖出

**优化方案3：分批出场**
- RSI > 80时减仓50%
- RSI > 85时再减仓30%
- 保留20%仓位等待趋势反转确认

**建议采用方案2**，因为它提供了更可靠的卖出信号。
"""
        },
        
        {
            "title": "场景3：策略组合讨论",
            "user_input": """
我现在有三个策略：
1. 均线突破策略（中期）
2. RSI超买超卖策略（短期）
3. 布林带挤压策略（短期）

请帮我分析如何组合使用这些策略。
""",
            "ai_response": """
很好的策略组合！建议按以下方式整合：

**资金分配：**
- 均线突破策略：50%（主策略）
- RSI策略：30%（辅助策略）
- 布林带策略：20%（机会策略）

**使用场景：**
- 趋势市场：主要使用均线突破策略
- 震荡市场：重点使用RSI和布林带策略
- 突破前夕：布林带挤压提供预警信号

**协同规则：**
1. 当均线策略给出信号时，用RSI确认是否过热
2. 布林带挤压后的突破，可以加大均线策略的仓位
3. 三个策略同时看多/看空时，可以适当增加总仓位

**风险控制：**
- 单个策略最大回撤不超过5%
- 总体组合最大回撤不超过10%
"""
        }
    ]
    
    for scenario in scenarios:
        print(f"🎯 {scenario['title']}")
        print("-" * 50)
        print("👤 用户输入:")
        print(scenario['user_input'])
        print("\n🤖 AI助手回复:")
        print(scenario['ai_response'])
        print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    print("🚀 交易规则提取系统演示")
    print("=" * 70)
    
    # 演示对话式分析
    demo_conversation_analysis()
    
    # 演示规则分析
    demo_rule_analysis()
    
    # 演示对话场景
    demo_conversation_scenarios()
    
    print("\n✅ 演示完成！")
    print("\n📚 接下来你可以：")
    print("1. 将PDF文件放入 raw_books/ 目录")
    print("2. 运行 python extract_trading_rules.py --mode full --ai")
    print("3. 在对话中使用生成的提示来分析你的交易书籍")
    print("4. 根据提取的规则生成可执行的策略代码") 