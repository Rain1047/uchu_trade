# 交易规则提取系统使用指南

## 系统概述

这是一个完整的交易策略提取系统，可以从交易书籍PDF中自动提取交易规则，并生成可执行的策略代码。系统支持对话式分析，让你可以通过与AI助手对话来精确提取和优化交易规则。

## 快速开始

### 1. 准备工作

```bash
# 进入策略材料目录
cd backend/strategy_center/strategy_materials

# 安装依赖
pip install PyPDF2 pdfplumber pymupdf pandas numpy

# 检查目录结构
ls -la
```

### 2. 放置PDF文件

将你的交易书籍PDF文件放入 `raw_books/` 目录，文件命名规范：

```
raw_books/
├── 股票作手回忆录_杰西利佛摩尔_short_term.pdf
├── 聪明的投资者_本杰明格雷厄姆_long_term.pdf
├── 海龟交易法则_柯蒂斯费思_medium_term.pdf
└── 日本蜡烛图技术_史蒂夫尼森_short_term.pdf
```

命名格式：`{书名}_{作者}_{交易类型}.pdf`
- 交易类型：`long_term`（长期）、`medium_term`（中期）、`short_term`（短期）

### 3. 运行系统

#### 方式一：自动化处理

```bash
# 运行完整流程（基础模式）
python extract_trading_rules.py --mode full

# 运行完整流程（AI增强模式）
python extract_trading_rules.py --mode full --ai
```

#### 方式二：分步处理

```bash
# 步骤1：提取PDF文本
python extract_trading_rules.py --mode pdf

# 步骤2：提取交易规则
python extract_trading_rules.py --mode rules --ai

# 步骤3：生成策略代码
python extract_trading_rules.py --mode strategies
```

## 对话式规则提取

### 核心理念

我们的系统设计支持在**对话框中完成整个规则提取过程**，通过与AI助手的多轮对话来：

1. **逐步分析**：从粗略理解到精确提取
2. **交互式优化**：根据你的反馈调整提取结果
3. **上下文理解**：保持对话连贯性，积累分析经验

### 对话工作流程

#### 阶段1：初步分析

```bash
# 生成对话提示
python extract_trading_rules.py --mode prompt
```

系统会生成如下的对话起始提示：

```
我有一段交易书籍的文本，想要提取其中的交易规则。请帮我分析这段文本：

```
当价格突破20日移动平均线，且RSI指标大于50时，这通常是一个买入信号。
但我们还需要确认成交量是否放大，以及整体市场趋势是否向上...
```

请先告诉我这段文本主要讨论的是什么交易策略或方法？
```

#### 阶段2：深度规则提取

基于AI的初步分析，继续深入：

```
很好！现在请帮我从这段文本中提取具体的交易规则，包括：

1. 入场条件：什么时候买入？
2. 出场条件：什么时候卖出？
3. 风险控制：如何设置止损？
4. 资金管理：如何控制仓位？

请尽可能详细和具体。
```

#### 阶段3：参数化提取

```
现在请帮我识别这些规则中的具体参数，比如：
- 技术指标的周期设置
- 止损止盈的百分比
- 仓位大小的限制
- 时间框架的选择

这些参数对于实际应用很重要。
```

#### 阶段4：代码实现

```
最后，请帮我把这些规则整理成可以程序化实现的格式，包括：
- 明确的条件判断逻辑
- 具体的数值参数
- 优先级和执行顺序
- 特殊情况的处理

格式要求是结构化的JSON。
```

### 实际对话示例

#### 示例1：分析海龟交易法则

**用户**：
```
我想分析《海龟交易法则》中的策略，这段文本是：

"海龟交易法则的核心是趋势跟踪。当价格突破20日高点时买入，
当价格跌破10日低点时卖出。仓位大小基于账户余额的2%风险来计算，
止损设在价格跌破2个ATR的位置。"

请帮我提取交易规则。
```

**AI助手**：
```json
{
  "strategy_analysis": {
    "name": "海龟交易突破策略",
    "type": "趋势跟踪",
    "timeframe": "中期",
    "entry_rules": [
      {
        "name": "突破买入",
        "conditions": ["价格突破20日最高价"],
        "indicators": ["20日最高价"],
        "parameters": {"lookback_period": 20}
      }
    ],
    "exit_rules": [
      {
        "name": "突破卖出",
        "conditions": ["价格跌破10日最低价"],
        "indicators": ["10日最低价"],
        "parameters": {"lookback_period": 10}
      }
    ],
    "risk_management": {
      "position_sizing": "账户余额2%风险",
      "stop_loss": "2个ATR距离",
      "risk_percent": 2.0
    }
  }
}
```

#### 示例2：优化和细化

**用户**：
```
这个分析很好，但我想进一步细化止损逻辑。在原文中还提到了
"如果价格在入场后立即反向，应该考虑减少仓位"。
请帮我把这个规则也加入进去。
```

**AI助手**：
```json
{
  "enhanced_rules": {
    "exit_rules": [
      {
        "name": "突破卖出",
        "conditions": ["价格跌破10日最低价"],
        "priority": 1
      },
      {
        "name": "ATR止损",
        "conditions": ["价格跌破入场价 - 2*ATR"],
        "priority": 2
      },
      {
        "name": "快速反向保护",
        "conditions": [
          "入场后5根K线内",
          "价格反向超过1个ATR"
        ],
        "action": "减少仓位50%",
        "priority": 3
      }
    ]
  }
}
```

## 高级功能

### 1. 批量文本分析

如果你有多段文本需要分析，可以创建一个文本文件列表：

```python
# 在对话中使用
texts = [
    "趋势交易规则第一章内容...",
    "趋势交易规则第二章内容...",
    "风险管理章节内容..."
]

for i, text in enumerate(texts):
    print(f"分析第{i+1}段文本：")
    print(f"请分析这段关于{['趋势判断', '入场时机', '风险控制'][i]}的内容")
    print(text)
```

### 2. 规则验证和测试

提取规则后，你可以在对话中验证逻辑：

```
基于我们提取的规则，请帮我验证以下场景：

场景1：价格突破20日高点，但成交量很小
场景2：RSI已经超过80，但价格仍在突破
场景3：大盘在下跌，但个股符合买入条件

这些情况下策略应该如何处理？
```

### 3. 参数优化建议

```
根据提取的规则，请建议哪些参数可以优化：

1. 20日突破周期是否合适？
2. 2%的风险比例是否保守？
3. ATR倍数设置为2是否合理？

请给出优化建议和理由。
```

## 输出文件说明

### 处理后的文件结构

```
strategy_materials/
├── raw_books/                 # 原始PDF文件
├── extracted_text/            # 提取的文本内容
│   ├── 股票作手回忆录_杰西利佛摩尔_short_term.txt
│   └── 聪明的投资者_本杰明格雷厄姆_long_term.txt
├── processed_rules/           # 处理后的规则
│   ├── 股票作手回忆录_杰西利佛摩尔_short_term_rules.json
│   ├── 股票作手回忆录_杰西利佛摩尔_short_term_ai_analysis.json
│   └── extraction_summary.json
├── final_strategies/          # 生成的策略代码
│   ├── strategy_股票作手回忆录_杰西利佛摩尔_short_term.py
│   ├── strategy_股票作手回忆录_杰西利佛摩尔_short_term_config.json
│   └── generation_summary.json
└── extraction_report.json    # 最终处理报告
```

### 规则文件格式

#### 基础规则文件（*_rules.json）

```json
{
  "processed_files": [
    {
      "filename": "example.txt",
      "rule_count": 15,
      "rules": [
        {
          "rule_id": "abc123",
          "name": "RSI超买卖出",
          "type": "exit",
          "timeframe": "short",
          "conditions": ["RSI > 70", "持仓超过3天"],
          "signals": ["技术指标背离"],
          "parameters": {"rsi_threshold": 70},
          "source": "example.txt",
          "confidence": 0.85,
          "description": "当RSI指标超过70时考虑卖出..."
        }
      ]
    }
  ],
  "total_rules": 15,
  "rules_by_type": {"entry": 8, "exit": 5, "filter": 2},
  "rules_by_timeframe": {"short": 10, "medium": 3, "long": 2}
}
```

#### AI增强分析文件（*_ai_analysis.json）

```json
{
  "entry_rules": [
    {
      "name": "均线突破买入",
      "conditions": ["价格突破20日均线", "成交量放大"],
      "timeframe": "medium",
      "indicators": ["MA20", "Volume"],
      "parameters": {"ma_period": 20, "volume_ratio": 1.5},
      "market_context": "牛市",
      "confidence": 0.90
    }
  ],
  "exit_rules": [...],
  "filter_rules": [...],
  "summary": {
    "total_entry_rules": 5,
    "total_exit_rules": 3,
    "total_filter_rules": 2,
    "average_confidence": 0.82
  }
}
```

### 策略代码示例

生成的策略文件是完整的Python类：

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class StrategyExampleBook:
    """
    基于《示例交易书籍》提取的交易策略
    
    来源: 示例交易书籍
    时间框架: medium
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.name = "strategy_example_book"
        self.timeframe = "medium"
        self.parameters = parameters or {
            "risk_percent": 2.0,
            "stop_loss_percent": 5.0,
            "take_profit_percent": 10.0
        }
        
        # 策略状态
        self.position = 0
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
    
    def check_entry_conditions(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """检查入场条件"""
        # 具体的入场逻辑
        pass
    
    def check_exit_conditions(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """检查出场条件"""
        # 具体的出场逻辑
        pass
```

## 最佳实践

### 1. 文本准备

- **清理文本**：确保PDF转换后的文本格式正确
- **分章节处理**：对于长文档，建议分章节进行分析
- **标注重点**：在对话中明确指出你最关心的规则类型

### 2. 对话技巧

- **逐步细化**：从宏观理解到具体参数，逐步深入
- **多轮验证**：同一个规则可以从不同角度验证
- **实例验证**：用具体的市场场景来测试规则逻辑

### 3. 规则优化

- **参数调试**：提取规则后，在对话中讨论参数优化
- **组合测试**：讨论多个规则的组合使用效果
- **风险控制**：重点关注风险管理规则的完整性

### 4. 代码集成

- **规则映射**：确保提取的规则能够映射到代码逻辑
- **参数配置**：验证所有参数都有合理的默认值
- **错误处理**：考虑异常情况的处理逻辑

## 故障排除

### 常见问题

1. **PDF文本提取失败**
   - 检查PDF文件是否损坏
   - 尝试不同的PDF处理库
   - 手动转换为文本文件

2. **规则提取质量不高**
   - 使用AI增强模式（--ai参数）
   - 在对话中提供更多上下文
   - 分段处理长文本

3. **生成的策略代码有错误**
   - 检查规则文件的格式
   - 验证参数的数据类型
   - 手动调整策略模板

### 调试技巧

```bash
# 启用详细日志
export PYTHONPATH=/Users/rain/PycharmProjects/uchu_trade/backend/strategy_center/strategy_materials

# 逐步调试
python -c "
from tools.pdf_processor import PDFProcessor
processor = PDFProcessor('raw_books', 'extracted_text')
print(processor.process_all_pdfs())
"
```

## 进阶应用

### 1. 自定义提示模板

你可以在对话中创建自定义的分析提示：

```
请按照以下模板分析交易规则：

模板：
- 策略名称：
- 适用市场：
- 时间周期：
- 入场条件：
  1. 技术条件：
  2. 基本面条件：
  3. 市场环境：
- 出场条件：
  1. 止盈：
  2. 止损：
  3. 时间止损：
- 风险控制：
- 仓位管理：
```

### 2. 多策略组合

在对话中讨论如何组合多个策略：

```
我已经提取了3个不同的策略：
1. 趋势跟踪策略（中长期）
2. 均值回归策略（短期）
3. 突破策略（中期）

请帮我分析：
1. 这些策略是否可以组合使用？
2. 如何分配不同策略的资金比例？
3. 在什么市场环境下使用哪个策略？
```

### 3. 实时优化

```
根据最近的市场表现，我想优化之前提取的规则：

原规则：RSI > 70时卖出
观察：最近强势股RSI经常超过80仍在上涨

请建议如何修改这个规则，并考虑：
1. 增加额外的确认条件
2. 动态调整RSI阈值
3. 结合其他指标
```

## 总结

这个系统的核心优势是**支持对话式的规则提取和优化**。通过与AI助手的多轮对话，你可以：

1. **精确理解**书籍内容的交易逻辑
2. **逐步提取**完整的交易规则体系
3. **实时优化**规则参数和逻辑
4. **快速生成**可执行的策略代码

记住，最好的规则提取不是一次性完成的，而是通过持续的对话和优化来实现的。利用这个系统，你可以将交易大师的智慧转化为可执行的算法交易策略。 