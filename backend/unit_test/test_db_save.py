#!/usr/bin/env python3
"""
测试数据库保存功能
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.backtest_center.enhanced_backtest_runner import EnhancedBacktestRunner

def test_database_save():
    """测试数据库保存功能"""
    print("🧪 测试数据库保存功能")
    print("=" * 50)
    
    runner = EnhancedBacktestRunner()
    
    # 运行一个简单的回测
    print("🎯 运行简单回测...")
    result = runner.run_complete_backtest(
        entry_strategy="sma_cross_entry_long_strategy",
        exit_strategy="dbb_exit_long_strategy",
        symbols=["BTC-USDT"],  # 只测试一个交易对
        timeframe="4h",
        description="数据库保存测试",
        save_to_db=True
    )
    
    if result["success"]:
        print("✅ 回测成功完成!")
        print(f"配置键: {result['config_key']}")
        
        # 检查数据库中的记录
        print("\n💾 检查数据库记录...")
        from backend.data_object_center.backtest_result import BacktestResult
        
        # 获取最近的记录
        recent_results = BacktestResult.list_all()[:5]  # 获取最近5条记录
        
        print(f"数据库中最近的 {len(recent_results)} 条记录:")
        for i, record in enumerate(recent_results, 1):
            print(f"  {i}. {record.symbol} - {record.strategy_name} - {record.test_finished_time}")
            print(f"     交易次数: {record.transaction_count}, 收益率: {record.profit_rate:.2f}%")
        
        print("\n🎉 数据库保存测试完成!")
        
    else:
        print(f"❌ 回测失败: {result['error']}")

if __name__ == "__main__":
    test_database_save() 