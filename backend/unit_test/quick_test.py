#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.backtest_center.universal_backtest_engine import universal_engine
from backend.data_object_center.backtest_config import BacktestConfig

def main():
    print("🚀 快速回测测试")
    print("=" * 50)
    
    # 创建配置
    config = BacktestConfig(
        entry_strategy='dbb_entry_long_strategy',
        exit_strategy='dbb_exit_long_strategy',
        symbols=['BTC-USDT'],
        timeframe='4h',  # 使用实际存在的时间框架
        description='快速测试'
    )
    
    print(f"配置创建成功: {config.get_display_name()}")
    print(f"配置键: {config.generate_key()}")
    
    # 运行回测
    print("\n正在运行回测...")
    result = universal_engine.run_backtest(config)
    
    print("\n✅ 回测完成!")
    print(f"结果键: {result.config_key}")
    print(f"交易对数量: {result.total_symbols}")
    print(f"平均收益率: {result.avg_return:.2%}")
    print(f"总交易次数: {result.total_trades_all}")
    print(f"平均胜率: {result.avg_win_rate:.1%}")
    
    if result.individual_results:
        print(f"最佳交易对: {result.best_symbol} ({result.best_return:.2%})")
        print(f"最差交易对: {result.worst_symbol} ({result.worst_return:.2%})")
        
        print("\n📈 详细结果:")
        for symbol_result in result.individual_results:
            print(f"  {symbol_result.symbol}:")
            print(f"    收益率: {symbol_result.total_return:.2%}")
            print(f"    交易次数: {symbol_result.total_trades}")
            print(f"    胜率: {symbol_result.win_rate:.1%}")
            print(f"    最大回撤: {symbol_result.max_drawdown:.2%}")
            print(f"    夏普比率: {symbol_result.sharpe_ratio:.2f}")
    
    # 查看缓存
    print(f"\n📦 缓存中的结果数量: {len(universal_engine.results_cache)}")
    for key, cached_result in universal_engine.results_cache.items():
        print(f"  {key}: {cached_result.config.get_display_name()}")

if __name__ == "__main__":
    main() 