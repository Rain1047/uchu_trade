# 交易策略材料处理系统

## 目录结构

```
strategy_materials/
├── raw_books/          # 原始书籍文件 (PDF, EPUB等)
├── extracted_text/     # 提取的文本内容
├── processed_rules/    # 处理后的交易规则
├── final_strategies/   # 最终的策略代码
└── tools/             # 处理工具
```

## 使用流程

### 1. 准备阶段
- 将交易书籍PDF文件放入 `raw_books/` 目录
- 确保文件命名规范：`{书名}_{作者}_{类型}.pdf`
  - 类型：long_term（长期）, medium_term（中期）, short_term（短期）

### 2. 文本提取阶段
- 使用PDF处理工具将书籍内容转换为文本
- 提取的文本保存到 `extracted_text/` 目录

### 3. 规则提取阶段
- 使用AI分析文本内容
- 识别并提取交易规则、信号、条件
- 按照时间框架分类

### 4. 规则处理阶段
- 将提取的规则结构化
- 去重和合并相似规则
- 验证规则的逻辑性

### 5. 策略生成阶段
- 将规则转换为可执行的策略代码
- 集成到现有的策略框架中

## 支持的书籍类型

- **长期交易**：价值投资、基本面分析
- **中期交易**：趋势跟踪、技术分析
- **短期交易**：日内交易、高频策略

## 输出格式

提取的规则将以以下格式保存：

```json
{
  "rule_id": "unique_identifier",
  "name": "规则名称",
  "type": "entry/exit/filter",
  "timeframe": "long/medium/short",
  "conditions": [],
  "signals": [],
  "parameters": {},
  "source": "书籍来源",
  "confidence": 0.85
}
``` 