#!/usr/bin/env python3
"""
测试增强的K线数据管理器
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.data_center.kline_data.enhanced_kline_manager import (
    EnhancedKlineManager, 
    CommonIndicators,
    create_indicator_request
)

def test_basic_functionality():
    """测试基本功能"""
    print("🔍 测试基本功能")
    print("=" * 50)
    
    # 创建管理器
    manager = EnhancedKlineManager()
    
    # 获取可用交易对
    symbols = manager.get_available_symbols()
    print(f"📊 可用交易对 ({len(symbols)}): {symbols}")
    
    if not symbols:
        print("❌ 没有找到可用的交易对数据")
        return False
    
    # 测试第一个交易对
    symbol = symbols[0]
    print(f"\n🎯 测试交易对: {symbol}")
    
    # 获取可用时间框架
    timeframes = manager.get_available_timeframes(symbol)
    print(f"⏰ 可用时间框架: {timeframes}")
    
    if not timeframes:
        print(f"❌ {symbol} 没有可用的时间框架")
        return False
    
    # 测试第一个时间框架
    timeframe = timeframes[0]
    print(f"\n📈 测试时间框架: {timeframe}")
    
    # 获取数据信息
    info = manager.get_data_info(symbol, timeframe)
    if info:
        print(f"📋 数据信息:")
        print(f"  - 文件路径: {info['filepath']}")
        print(f"  - 总记录数: {info['total_records']}")
        print(f"  - 文件大小: {info['file_size_mb']} MB")
        print(f"  - 列名: {info['columns']}")
        print(f"  - 最后修改: {info['last_modified']}")
    
    return True

def test_data_loading():
    """测试数据加载"""
    print("\n🔄 测试数据加载")
    print("=" * 50)
    
    manager = EnhancedKlineManager()
    symbols = manager.get_available_symbols()
    
    if not symbols:
        print("❌ 没有可用的交易对")
        return False
    
    symbol = symbols[0]
    timeframes = manager.get_available_timeframes(symbol)
    
    if not timeframes:
        print(f"❌ {symbol} 没有可用的时间框架")
        return False
    
    timeframe = timeframes[0]
    
    # 加载原始数据
    print(f"📥 加载 {symbol} {timeframe} 原始数据...")
    df = manager.load_raw_data(symbol, timeframe)
    
    if df is None:
        print("❌ 数据加载失败")
        return False
    
    print(f"✅ 数据加载成功!")
    print(f"  - 数据形状: {df.shape}")
    print(f"  - 列名: {list(df.columns)}")
    print(f"  - 索引类型: {type(df.index)}")
    print(f"  - 时间范围: {df.index.min()} 到 {df.index.max()}")
    
    # 显示前几行数据
    print(f"\n📊 前5行数据:")
    print(df.head())
    
    return True

def test_indicator_calculation():
    """测试指标计算"""
    print("\n🧮 测试指标计算")
    print("=" * 50)
    
    manager = EnhancedKlineManager()
    symbols = manager.get_available_symbols()
    
    if not symbols:
        print("❌ 没有可用的交易对")
        return False
    
    symbol = symbols[0]
    timeframes = manager.get_available_timeframes(symbol)
    
    if not timeframes:
        print(f"❌ {symbol} 没有可用的时间框架")
        return False
    
    timeframe = timeframes[0]
    
    # 定义要计算的指标
    indicators = [
        CommonIndicators.sma(20),
        CommonIndicators.ema(20),
        CommonIndicators.rsi(14),
        CommonIndicators.bollinger_upper(20, 2.0),
        CommonIndicators.bollinger_middle(20, 2.0),
        CommonIndicators.bollinger_lower(20, 2.0),
        CommonIndicators.adx(14),
    ]
    
    print(f"🎯 计算 {len(indicators)} 个指标...")
    
    # 获取带指标的数据
    df_with_indicators = manager.get_data_with_indicators(symbol, timeframe, indicators)
    
    if df_with_indicators is None:
        print("❌ 指标计算失败")
        return False
    
    print(f"✅ 指标计算成功!")
    print(f"  - 原始列数: {len([col for col in df_with_indicators.columns if col in ['open', 'high', 'low', 'close', 'volume']])}")
    print(f"  - 指标列数: {len(df_with_indicators.columns) - len([col for col in df_with_indicators.columns if col in ['open', 'high', 'low', 'close', 'volume']])}")
    print(f"  - 总列数: {len(df_with_indicators.columns)}")
    
    # 显示新增的指标列
    indicator_columns = [col for col in df_with_indicators.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
    print(f"\n📈 计算的指标:")
    for col in indicator_columns:
        non_null_count = df_with_indicators[col].count()
        print(f"  - {col}: {non_null_count} 个有效值")
    
    # 显示最后几行数据（包含指标）
    print(f"\n📊 最后5行数据（含指标）:")
    print(df_with_indicators.tail()[['close'] + indicator_columns[:3]])  # 只显示部分列
    
    return True

def test_caching():
    """测试缓存功能"""
    print("\n💾 测试缓存功能")
    print("=" * 50)
    
    manager = EnhancedKlineManager()
    symbols = manager.get_available_symbols()
    
    if not symbols:
        print("❌ 没有可用的交易对")
        return False
    
    symbol = symbols[0]
    timeframes = manager.get_available_timeframes(symbol)
    
    if not timeframes:
        print(f"❌ {symbol} 没有可用的时间框架")
        return False
    
    timeframe = timeframes[0]
    
    import time
    
    # 第一次加载（应该从文件读取）
    print(f"🔄 第一次加载 {symbol} {timeframe}...")
    start_time = time.time()
    df1 = manager.load_raw_data(symbol, timeframe)
    time1 = time.time() - start_time
    print(f"⏱️ 第一次加载耗时: {time1:.3f} 秒")
    
    # 第二次加载（应该从缓存读取）
    print(f"🔄 第二次加载 {symbol} {timeframe}...")
    start_time = time.time()
    df2 = manager.load_raw_data(symbol, timeframe)
    time2 = time.time() - start_time
    print(f"⏱️ 第二次加载耗时: {time2:.3f} 秒")
    
    # 验证数据一致性
    if df1 is not None and df2 is not None:
        if df1.equals(df2):
            print("✅ 缓存数据一致性验证通过")
            print(f"🚀 缓存加速比: {time1/time2:.1f}x")
        else:
            print("❌ 缓存数据不一致")
            return False
    
    # 测试指标缓存
    print(f"\n🧮 测试指标缓存...")
    indicators = [CommonIndicators.sma(20), CommonIndicators.rsi(14)]
    
    # 第一次计算指标
    start_time = time.time()
    df_with_indicators1 = manager.get_data_with_indicators(symbol, timeframe, indicators)
    time1 = time.time() - start_time
    print(f"⏱️ 第一次指标计算耗时: {time1:.3f} 秒")
    
    # 第二次计算指标（应该使用缓存）
    start_time = time.time()
    df_with_indicators2 = manager.get_data_with_indicators(symbol, timeframe, indicators)
    time2 = time.time() - start_time
    print(f"⏱️ 第二次指标计算耗时: {time2:.3f} 秒")
    
    if time2 < time1:
        print(f"🚀 指标缓存加速比: {time1/time2:.1f}x")
    
    return True

def test_timeframe_normalization():
    """测试时间框架标准化"""
    print("\n🕐 测试时间框架标准化")
    print("=" * 50)
    
    manager = EnhancedKlineManager()
    
    # 测试不同格式的时间框架
    test_cases = [
        ('1h', '1h'),
        ('1H', '1h'),
        ('4h', '4h'),
        ('4H', '4h'),
        ('1d', '1d'),
        ('1D', '1d'),
        ('invalid', None),
    ]
    
    for input_tf, expected_output in test_cases:
        config = manager.normalize_timeframe(input_tf)
        if expected_output is None:
            if config is None:
                print(f"✅ {input_tf} -> None (预期)")
            else:
                print(f"❌ {input_tf} -> {config.standard_name} (应该是 None)")
        else:
            if config and config.standard_name == expected_output:
                print(f"✅ {input_tf} -> {config.standard_name}")
            else:
                print(f"❌ {input_tf} -> {config.standard_name if config else None} (应该是 {expected_output})")
    
    return True

def main():
    """主测试函数"""
    print("🚀 增强K线数据管理器测试")
    print("=" * 60)
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("数据加载", test_data_loading),
        ("指标计算", test_indicator_calculation),
        ("缓存功能", test_caching),
        ("时间框架标准化", test_timeframe_normalization),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
    
    print(f"\n{'='*60}")
    print(f"🎯 测试总结: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！增强K线数据管理器工作正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main() 