#!/usr/bin/env python3
"""
通用回测系统测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.data_object_center.backtest_config import BacktestConfig
from backend.backtest_center.universal_backtest_engine import universal_engine
from backend._utils import LogConfig

# 设置日志
LogConfig.setup()
logger = LogConfig.get_logger(__name__)


def test_strategy_listing():
    """测试策略列表获取"""
    print("=== 测试策略列表获取 ===")
    try:
        strategies = universal_engine.get_available_strategies()
        print(f"可用策略类型: {list(strategies.keys())}")
        
        for strategy_type, strategy_list in strategies.items():
            print(f"\n{strategy_type.upper()} 策略:")
            for strategy in strategy_list:
                print(f"  - {strategy['name']}: {strategy.get('desc', '无描述')}")
        
        return True
    except Exception as e:
        print(f"获取策略列表失败: {e}")
        return False


def test_symbol_listing():
    """测试交易对列表获取"""
    print("\n=== 测试交易对列表获取 ===")
    try:
        symbols = universal_engine.get_available_symbols()
        print(f"可用交易对: {symbols}")
        return True
    except Exception as e:
        print(f"获取交易对列表失败: {e}")
        return False


def test_config_creation():
    """测试配置创建和键生成"""
    print("\n=== 测试配置创建 ===")
    try:
        config = BacktestConfig(
            entry_strategy="dbb_entry_strategy",
            exit_strategy="dbb_exit_strategy", 
            filter_strategy="sma_diff_increasing_filter_strategy",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1h",
            initial_cash=100000.0,
            description="测试配置"
        )
        
        print(f"配置键: {config.generate_key()}")
        print(f"显示名称: {config.get_display_name()}")
        print(f"配置详情: {config.to_dict()}")
        
        return config
    except Exception as e:
        print(f"创建配置失败: {e}")
        return None


def test_single_backtest():
    """测试单个交易对回测"""
    print("\n=== 测试单个交易对回测 ===")
    try:
        config = BacktestConfig(
            entry_strategy="dbb_entry_strategy",
            exit_strategy="dbb_exit_strategy",
            symbols=["BTC-USDT"],
            timeframe="1h",
            initial_cash=50000.0,
            start_date="2024-01-01",
            end_date="2024-03-01",
            description="单个交易对测试"
        )
        
        print(f"开始回测: {config.get_display_name()}")
        summary = universal_engine.run_backtest(config)
        
        print(f"回测完成!")
        print(f"配置键: {summary.config_key}")
        print(f"测试交易对数量: {summary.total_symbols}")
        print(f"平均收益率: {summary.avg_return:.2%}")
        
        if summary.individual_results:
            result = summary.individual_results[0]
            print(f"详细结果:")
            print(f"  - 初始资金: ${result.initial_value:,.2f}")
            print(f"  - 最终资金: ${result.final_value:,.2f}")
            print(f"  - 总收益率: {result.total_return:.2%}")
            print(f"  - 总交易次数: {result.total_trades}")
            print(f"  - 胜率: {result.win_rate:.1f}%")
            print(f"  - 信号执行率: {result.signal_execution_rate:.1f}%")
        
        return True
    except Exception as e:
        print(f"单个回测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_backtest():
    """测试多个交易对回测"""
    print("\n=== 测试多个交易对回测 ===")
    try:
        config = BacktestConfig(
            entry_strategy="dbb_entry_strategy",
            exit_strategy="dbb_exit_strategy",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1h",
            initial_cash=100000.0,
            start_date="2024-01-01",
            end_date="2024-02-01",
            description="多交易对测试"
        )
        
        print(f"开始多交易对回测: {config.get_display_name()}")
        summary = universal_engine.run_backtest(config)
        
        print(f"多交易对回测完成!")
        print(f"测试交易对数量: {summary.total_symbols}")
        print(f"平均收益率: {summary.avg_return:.2%}")
        print(f"最佳交易对: {summary.best_symbol} ({summary.best_return:.2%})")
        print(f"最差交易对: {summary.worst_symbol} ({summary.worst_return:.2%})")
        print(f"总交易次数: {summary.total_trades_all}")
        print(f"平均胜率: {summary.avg_win_rate:.1f}%")
        
        return True
    except Exception as e:
        print(f"多交易对回测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_functionality():
    """测试缓存功能"""
    print("\n=== 测试缓存功能 ===")
    try:
        # 创建相同配置
        config = BacktestConfig(
            entry_strategy="dbb_entry_strategy",
            exit_strategy="dbb_exit_strategy",
            symbols=["BTC-USDT"],
            timeframe="1h",
            description="缓存测试"
        )
        
        print("第一次运行回测...")
        summary1 = universal_engine.run_backtest(config)
        
        print("第二次运行相同配置（应该从缓存获取）...")
        summary2 = universal_engine.run_backtest(config)
        
        if summary1.config_key == summary2.config_key:
            print("✅ 缓存功能正常工作")
            return True
        else:
            print("❌ 缓存功能异常")
            return False
            
    except Exception as e:
        print(f"缓存测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始通用回测系统测试")
    
    tests = [
        ("策略列表获取", test_strategy_listing),
        ("交易对列表获取", test_symbol_listing), 
        ("配置创建", test_config_creation),
        ("单个交易对回测", test_single_backtest),
        ("多个交易对回测", test_multi_backtest),
        ("缓存功能", test_cache_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"正在运行: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: ❌ 异常 - {e}")
    
    # 输出测试总结
    print(f"\n{'='*50}")
    print("测试总结")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！通用回测系统工作正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")


if __name__ == "__main__":
    main() 