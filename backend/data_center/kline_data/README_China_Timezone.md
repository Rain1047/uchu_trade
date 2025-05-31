# 中国时间8点边界K线数据获取机制

## 概述

本系统已支持按照中国时间8点作为每日K线的边界进行数据获取，确保日线数据的时间标准符合中国市场习惯。

## 工作原理

### 时间边界定义
- **日线数据（1d）**：每条记录代表从前一日中国时间8:00到当日中国时间8:00的24小时数据
- **其他时间框架**：保持标准UTC时间，不受8点边界影响

### 示例说明

假设获取5月31日的日线数据：
```
日期: 2025-05-31 08:00:00+08:00
实际时间范围: 2025-05-30 08:00:00 到 2025-05-31 08:00:00 (中国时间)
```

这意味着：
- **5月31日的数据** = 5月30日8:00 ~ 5月31日8:00的交易数据
- **5月30日的数据** = 5月29日8:00 ~ 5月30日8:00的交易数据
- **以此类推...**

## 技术实现

### 1. 时区转换过程
```python
# 输入: 2025-05-31
# 步骤1: 添加中国时间8点
china_time = 2025-05-31 08:00:00+08:00

# 步骤2: 转换为UTC时间（OKX API使用UTC）
utc_time = 2025-05-31 00:00:00+00:00

# 步骤3: 获取数据后转换显示时间
display_time = 2025-05-31 08:00:00+08:00
```

### 2. 文件输出格式
生成的CSV文件中，时间列显示为中国时间：
```csv
,open,high,low,close,volume,symbol
2025-05-31 08:00:00+08:00,105538.8,105565.4,103078.7,104554.2,5156.207859,Binance:BTCUSDT
```

## 使用方法

### 1. 直接使用OKX获取器
```python
from backend.data_center.kline_data.okx_kline_fetcher import OkxKlineFetcher

fetcher = OkxKlineFetcher("/path/to/data")

# 获取日线数据（自动应用8点边界）
df = fetcher.get_historical_data("BTC", "1d", 
                                start_date="2025-05-30", 
                                end_date="2025-05-31")

# 获取小时线数据（使用标准时间）
df_1h = fetcher.get_historical_data("BTC", "1h",
                                   start_date="2025-05-31",
                                   end_date="2025-05-31")
```

### 2. 通过数据管理器使用
```python
from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager

manager = EnhancedKlineManager()

# 自动使用OKX获取器（如果指定时间范围）
df = manager.load_raw_data("BTC", "1d", 
                          start_date="2025-05-30", 
                          end_date="2025-05-31")
```

### 3. 在回测中使用
回测系统会自动使用新的时间边界机制：
```python
# 回测配置
config = BacktestConfig(
    symbols=['BTC'],
    timeframe='1d',
    backtest_period='3m',  # 3个月
    # ... 其他参数
)

# 运行回测（自动应用中国时间8点边界）
result = universal_engine.run_backtest(config)
```

## 重要说明

### 1. 仅影响日线数据
- **1d（日线）**：应用中国时间8点边界
- **1h, 4h, 12h等**：使用标准UTC时间

### 2. 时区标识
- 生成的数据带有时区信息：`+08:00` 或 `CST`
- 确保时间戳的准确性和可追溯性

### 3. 向后兼容
- 现有代码无需修改
- 系统自动识别并应用新的时间边界

### 4. 数据一致性
- 同一交易日的数据始终对应相同的24小时时间窗口
- 避免了跨时区数据不一致的问题

## 验证方法

可以通过以下方式验证时间边界是否正确应用：

```python
# 运行测试
python backend/data_center/kline_data/okx_kline_fetcher.py

# 检查日志输出
# 应该看到类似输出：
# 时间范围调整:
#   输入: 2025-05-30 ~ 2025-05-31
#   中国时间: 2025-05-30 08:00:00+08:00 ~ 2025-05-31 08:00:00+08:00
#   UTC时间: 2025-05-30 00:00:00+00:00 ~ 2025-05-31 00:00:00+00:00
```

## 历史数据处理

对于已有的历史数据文件：
- 新系统优先使用OKX API获取实时数据
- 历史文件作为备用数据源
- 数据时间戳会自动标准化为中国时间显示

这确保了数据的一致性和准确性。 