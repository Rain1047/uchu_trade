#!/usr/bin/env python3
"""
查看通用回测系统的运行结果
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.backtest_center.universal_backtest_engine import universal_engine
from backend.backtest_center.backtest_config import BacktestConfig
import json
from datetime import datetime

def view_cached_results():
    """查看缓存的回测结果"""
    print("🔍 查看缓存的回测结果")
    print("=" * 60)
    
    if not universal_engine.results_cache:
        print("❌ 没有找到缓存的回测结果")
        return
    
    for i, (key, result) in enumerate(universal_engine.results_cache.items(), 1):
        print(f"\n📊 结果 #{i}")
        print(f"配置键: {key}")
        print(f"显示名称: {result.display_name}")
        print(f"交易对数量: {len(result.results)}")
        print(f"平均收益率: {result.avg_return:.2%}")
        print(f"总交易次数: {result.total_trades}")
        print(f"平均胜率: {result.avg_win_rate:.1%}")
        print(f"创建时间: {result.created_at}")
        
        if result.results:
            print("\n📈 各交易对详细结果:")
            for symbol, symbol_result in result.results.items():
                print(f"  {symbol}: 收益率 {symbol_result.total_return:.2%}, "
                      f"交易次数 {symbol_result.total_trades}, "
                      f"胜率 {symbol_result.win_rate:.1%}")
        
        print("-" * 60)

def view_available_strategies():
    """查看可用策略"""
    print("\n🎯 可用策略列表")
    print("=" * 60)
    
    strategies = universal_engine.get_available_strategies()
    
    for strategy_type, strategy_list in strategies.items():
        print(f"\n{strategy_type.upper()} 策略:")
        for strategy_name, strategy_desc in strategy_list.items():
            print(f"  - {strategy_name}: {strategy_desc}")

def view_available_symbols():
    """查看可用交易对"""
    print("\n💰 可用交易对")
    print("=" * 60)
    
    symbols = universal_engine.get_available_symbols()
    print(f"共 {len(symbols)} 个交易对:")
    for i, symbol in enumerate(symbols, 1):
        print(f"  {i:2d}. {symbol}")

def create_sample_config():
    """创建示例配置"""
    print("\n⚙️ 创建示例配置")
    print("=" * 60)
    
    config = BacktestConfig(
        entry_strategy="dbb_entry_strategy",
        exit_strategy="dbb_exit_strategy", 
        filter_strategy="sma_diff_increasing_filter_strategy",
        symbols=["BTC-USDT", "ETH-USDT"],
        timeframe="1h",
        description="示例配置 - 布林带策略"
    )
    
    print(f"配置键: {config.key}")
    print(f"显示名称: {config.display_name}")
    print(f"策略组合: {config.entry_strategy} + {config.exit_strategy} + {config.filter_strategy}")
    print(f"交易对: {', '.join(config.symbols)}")
    print(f"时间框架: {config.timeframe}")
    
    return config

def run_sample_backtest():
    """运行示例回测"""
    print("\n🚀 运行示例回测")
    print("=" * 60)
    
    config = create_sample_config()
    
    try:
        result = universal_engine.run_backtest(config)
        print(f"\n✅ 回测完成!")
        print(f"配置键: {result.key}")
        print(f"测试交易对数量: {len(result.results)}")
        print(f"平均收益率: {result.avg_return:.2%}")
        print(f"总交易次数: {result.total_trades}")
        print(f"平均胜率: {result.avg_win_rate:.1%}")
        
        if result.results:
            print(f"最佳交易对: {result.best_symbol} ({result.best_return:.2%})")
            print(f"最差交易对: {result.worst_symbol} ({result.worst_return:.2%})")
        
        return result
    except Exception as e:
        print(f"❌ 回测失败: {e}")
        return None

def main():
    """主函数"""
    print("🎯 通用回测系统 - 结果查看器")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看缓存的回测结果")
        print("2. 查看可用策略")
        print("3. 查看可用交易对")
        print("4. 运行示例回测")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            view_cached_results()
        elif choice == "2":
            view_available_strategies()
        elif choice == "3":
            view_available_symbols()
        elif choice == "4":
            run_sample_backtest()
        elif choice == "5":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main() 