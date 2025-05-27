# 通用回测系统使用指南

## 🎯 系统概述

通用回测系统是一个灵活的策略组合回测框架，支持：

- **灵活的策略组合**：入场策略 + 出场策略 + 过滤策略（可选）
- **多交易对并行回测**：一次性测试多个交易对
- **配置缓存机制**：相同配置自动复用结果
- **无需创建实例**：直接通过配置运行回测

## 🏗️ 系统架构

```
通用回测系统
├── BacktestConfig      # 回测配置类
├── UniversalBacktestEngine  # 回测引擎
├── BacktestResult      # 单个交易对结果
├── BacktestSummary     # 多交易对汇总结果
└── API接口             # RESTful API
```

## 📋 核心概念

### 1. 配置键（Config Key）
每个回测配置会生成唯一的配置键，格式：
```
入场策略_出场策略_过滤策略_交易对_时间窗口 → MD5哈希
```

### 2. 策略组合
- **入场策略**：决定何时买入
- **出场策略**：决定何时卖出  
- **过滤策略**：过滤入场信号（可选）

### 3. 结果缓存
相同配置的回测结果会被缓存，避免重复计算。

## 🚀 快速开始

### 1. Python API 使用

```python
from backend.data_object_center.backtest_config import BacktestConfig
from backend.backtest_center.universal_backtest_engine import universal_engine

# 创建回测配置
config = BacktestConfig(
    entry_strategy="dbb_entry_strategy",
    exit_strategy="dbb_exit_strategy", 
    filter_strategy="sma_diff_increasing_filter_strategy",  # 可选
    symbols=["BTC-USDT", "ETH-USDT", "BNB-USDT"],
    timeframe="1h",
    initial_cash=100000.0,
    risk_percent=2.0,
    start_date="2024-01-01",
    end_date="2024-03-01"
)

# 运行回测
summary = universal_engine.run_backtest(config)

# 查看结果
print(f"平均收益率: {summary.avg_return:.2%}")
print(f"最佳交易对: {summary.best_symbol}")
print(f"总交易次数: {summary.total_trades_all}")
```

### 2. REST API 使用

#### 获取可用策略
```bash
GET /api/universal-backtest/strategies
```

#### 获取可用交易对
```bash
GET /api/universal-backtest/symbols
```

#### 运行回测
```bash
POST /api/universal-backtest/run
Content-Type: application/json

{
    "entry_strategy": "dbb_entry_strategy",
    "exit_strategy": "dbb_exit_strategy",
    "filter_strategy": "sma_diff_increasing_filter_strategy",
    "symbols": ["BTC-USDT", "ETH-USDT"],
    "timeframe": "1h",
    "initial_cash": 100000.0,
    "start_date": "2024-01-01",
    "end_date": "2024-03-01"
}
```

#### 获取回测结果
```bash
GET /api/universal-backtest/results
GET /api/universal-backtest/results/{config_key}
```

## 📊 配置参数详解

### BacktestConfig 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| entry_strategy | str | ✅ | 入场策略名称 |
| exit_strategy | str | ✅ | 出场策略名称 |
| filter_strategy | str | ❌ | 过滤策略名称 |
| symbols | List[str] | ✅ | 交易对列表 |
| timeframe | str | ❌ | 时间窗口，默认"1h" |
| initial_cash | float | ❌ | 初始资金，默认100000 |
| risk_percent | float | ❌ | 风险百分比，默认2.0 |
| commission | float | ❌ | 手续费，默认0.001 |
| start_date | str | ❌ | 开始日期 YYYY-MM-DD |
| end_date | str | ❌ | 结束日期 YYYY-MM-DD |
| strategy_params | dict | ❌ | 策略参数 |

### 策略参数示例

```python
strategy_params = {
    "entry": {
        "bb_period": 20,
        "bb_std": 2.0
    },
    "exit": {
        "stop_loss": 0.02,
        "take_profit": 0.05
    },
    "filter": {
        "sma_period": 50
    }
}
```

## 📈 结果解读

### BacktestSummary（汇总结果）

```python
{
    "config_key": "abc123def456",
    "total_symbols": 3,
    "avg_return": 0.15,          # 平均收益率 15%
    "best_symbol": "BTC-USDT",
    "best_return": 0.25,         # 最佳收益率 25%
    "worst_symbol": "ETH-USDT", 
    "worst_return": 0.05,        # 最差收益率 5%
    "total_trades_all": 150,     # 总交易次数
    "avg_win_rate": 65.5,        # 平均胜率 65.5%
    "avg_sharpe": 1.2,           # 平均夏普比率
    "individual_results": [...]   # 各交易对详细结果
}
```

### BacktestResult（单个交易对结果）

```python
{
    "symbol": "BTC-USDT",
    "total_return": 0.25,        # 总收益率 25%
    "annual_return": 0.45,       # 年化收益率 45%
    "sharpe_ratio": 1.5,         # 夏普比率
    "max_drawdown": 0.08,        # 最大回撤 8%
    "total_trades": 50,          # 交易次数
    "win_rate": 70.0,            # 胜率 70%
    "signal_execution_rate": 85.0 # 信号执行率 85%
}
```

## 🔧 高级功能

### 1. 批量回测

```python
# 测试多种策略组合
strategies = [
    ("dbb_entry_strategy", "dbb_exit_strategy"),
    ("ma_cross_entry", "trailing_stop_exit"),
    ("rsi_entry", "profit_target_exit")
]

results = []
for entry, exit in strategies:
    config = BacktestConfig(
        entry_strategy=entry,
        exit_strategy=exit,
        symbols=["BTC-USDT", "ETH-USDT"],
        timeframe="1h"
    )
    summary = universal_engine.run_backtest(config)
    results.append(summary)

# 比较结果
best_config = max(results, key=lambda x: x.avg_return)
```

### 2. 参数优化

```python
# 测试不同参数组合
risk_levels = [1.0, 2.0, 3.0, 5.0]
results = {}

for risk in risk_levels:
    config = BacktestConfig(
        entry_strategy="dbb_entry_strategy",
        exit_strategy="dbb_exit_strategy",
        symbols=["BTC-USDT"],
        risk_percent=risk
    )
    summary = universal_engine.run_backtest(config)
    results[risk] = summary.avg_return

# 找到最优风险水平
optimal_risk = max(results, key=results.get)
```

### 3. 时间窗口分析

```python
# 测试不同时间段
time_periods = [
    ("2023-01-01", "2023-06-30"),  # 上半年
    ("2023-07-01", "2023-12-31"),  # 下半年
    ("2024-01-01", "2024-06-30")   # 今年上半年
]

for start, end in time_periods:
    config = BacktestConfig(
        entry_strategy="dbb_entry_strategy",
        exit_strategy="dbb_exit_strategy",
        symbols=["BTC-USDT"],
        start_date=start,
        end_date=end
    )
    summary = universal_engine.run_backtest(config)
    print(f"{start} ~ {end}: {summary.avg_return:.2%}")
```

## 🧪 测试和验证

运行测试脚本：

```bash
cd backend/backtest_center
python test_universal_backtest.py
```

测试包括：
- ✅ 策略列表获取
- ✅ 交易对列表获取  
- ✅ 配置创建和键生成
- ✅ 单个交易对回测
- ✅ 多个交易对回测
- ✅ 缓存功能验证

## 🚨 注意事项

1. **数据依赖**：确保有足够的历史数据
2. **策略注册**：新策略需要在 `strategy_registry.py` 中注册
3. **内存管理**：大量交易对回测时注意内存使用
4. **并发限制**：默认最多4个并发回测任务
5. **缓存清理**：定期清理不需要的缓存结果

## 🔄 与现有系统的兼容性

新系统完全兼容现有的回测框架：
- 复用现有的 `BacktestSystem` 和 `StrategyForBacktest`
- 兼容现有的策略注册机制
- 保持现有的数据格式和分析器

## 🎉 优势总结

1. **灵活性**：无需创建实例，直接配置运行
2. **效率**：并行处理多交易对，缓存避免重复计算
3. **可扩展**：易于添加新策略和新功能
4. **易用性**：简洁的API和配置方式
5. **兼容性**：与现有系统无缝集成

---

通过这个通用回测系统，你可以快速测试各种策略组合，找到最优的交易策略！🚀 