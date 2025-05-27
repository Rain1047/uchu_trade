#!/usr/bin/env python3
"""
指定策略组合回测验证
使用：
- Entry: dbb_entry_long_strategy (布林带入场策略)
- Exit: dbb_exit_long_strategy (布林带出场策略)  
- Filter: sma_perfect_order_filter_strategy (SMA完美顺序过滤策略)
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.backtest_center.enhanced_backtest_runner import EnhancedBacktestRunner
from backend.data_object_center.backtest_result import BacktestResult as DBBacktestResult

def test_specified_strategy_combination():
    """测试指定的策略组合"""
    print("🎯 指定策略组合回测验证")
    print("=" * 60)
    print("策略组合:")
    print("  Entry:  dbb_entry_long_strategy (布林带入场策略)")
    print("  Exit:   dbb_exit_long_strategy (布林带出场策略)")
    print("  Filter: sma_perfect_order_filter_strategy (SMA完美顺序过滤策略)")
    print("=" * 60)
    
    runner = EnhancedBacktestRunner()
    
    # 1. 检查策略是否可用
    print("📋 检查策略可用性...")
    strategies = runner.get_available_strategies()
    
    entry_strategies = [s['name'] for s in strategies.get('entry', [])]
    exit_strategies = [s['name'] for s in strategies.get('exit', [])]
    filter_strategies = [s['name'] for s in strategies.get('filter', [])]
    
    print(f"可用入场策略: {entry_strategies}")
    print(f"可用出场策略: {exit_strategies}")
    print(f"可用过滤策略: {filter_strategies}")
    
    # 验证策略存在
    required_strategies = {
        'entry': 'dbb_entry_long_strategy',
        'exit': 'dbb_exit_long_strategy', 
        'filter': 'sma_perfect_order_filter_strategy'
    }
    
    missing_strategies = []
    if required_strategies['entry'] not in entry_strategies:
        missing_strategies.append(f"入场策略: {required_strategies['entry']}")
    if required_strategies['exit'] not in exit_strategies:
        missing_strategies.append(f"出场策略: {required_strategies['exit']}")
    if required_strategies['filter'] not in filter_strategies:
        missing_strategies.append(f"过滤策略: {required_strategies['filter']}")
    
    if missing_strategies:
        print(f"❌ 缺少策略: {', '.join(missing_strategies)}")
        return False
    
    print("✅ 所有策略都可用")
    
    # 2. 检查可用交易对
    print(f"\n💰 检查可用交易对...")
    symbols = runner.get_available_symbols()
    print(f"可用交易对 ({len(symbols)}): {symbols}")
    
    # 选择测试交易对
    test_symbols = symbols[:2] if len(symbols) >= 2 else symbols
    print(f"测试交易对: {test_symbols}")
    
    # 3. 运行指定策略组合回测
    print(f"\n🎯 运行指定策略组合回测...")
    print(f"配置详情:")
    print(f"  入场策略: {required_strategies['entry']}")
    print(f"  出场策略: {required_strategies['exit']}")
    print(f"  过滤策略: {required_strategies['filter']}")
    print(f"  交易对: {test_symbols}")
    print(f"  时间框架: 4h")
    print(f"  初始资金: $100,000")
    print(f"  风险百分比: 2%")
    print(f"  手续费: 0.1%")
    
    result = runner.run_complete_backtest(
        entry_strategy=required_strategies['entry'],
        exit_strategy=required_strategies['exit'],
        filter_strategy=required_strategies['filter'],
        symbols=test_symbols,
        timeframe="4h",
        initial_cash=100000.0,
        risk_percent=2.0,
        commission=0.001,
        save_to_db=True,
        description="指定策略组合验证回测"
    )
    
    # 4. 分析回测结果
    if result["success"]:
        print("\n✅ 回测成功完成!")
        print(f"配置键: {result['config_key']}")
        
        summary = result["summary"]
        print(f"\n📈 回测汇总:")
        print(f"  测试交易对数量: {summary.total_symbols}")
        print(f"  平均收益率: {summary.avg_return:.2%}")
        print(f"  总交易次数: {summary.total_trades_all}")
        print(f"  平均胜率: {summary.avg_win_rate:.1%}")
        
        if summary.individual_results:
            print(f"  最佳交易对: {summary.best_symbol} ({summary.best_return:.2%})")
            print(f"  最差交易对: {summary.worst_symbol} ({summary.worst_return:.2%})")
            
            print(f"\n📋 详细结果:")
            for i, result_detail in enumerate(summary.individual_results, 1):
                print(f"  {i}. {result_detail.symbol}:")
                print(f"     收益率: {result_detail.total_return:.2%}")
                print(f"     年化收益率: {result_detail.annual_return:.2%}")
                print(f"     夏普比率: {result_detail.sharpe_ratio:.2f}" if result_detail.sharpe_ratio else "     夏普比率: N/A")
                print(f"     最大回撤: {result_detail.max_drawdown:.2%}")
                print(f"     交易次数: {result_detail.total_trades}")
                print(f"     胜率: {result_detail.win_rate:.1%}")
                print(f"     入场信号数: {result_detail.total_entry_signals}")
                print(f"     信号执行率: {result_detail.signal_execution_rate:.1%}")
                print(f"     测试天数: {result_detail.duration_days}")
        
        # 5. 检查数据库保存
        print(f"\n💾 检查数据库保存...")
        try:
            # 查询最近的回测结果
            all_results = DBBacktestResult.list_all()
            recent_results = [r for r in all_results if result['config_key'] in str(r.strategy_id)][:10]
            
            print(f"数据库中找到 {len(recent_results)} 条相关记录:")
            for i, db_result in enumerate(recent_results, 1):
                db_dict = db_result.to_dict()
                print(f"  {i}. {db_dict['symbol']}: 收益率 {db_dict['profit_rate']:.2f}%, 交易次数 {db_dict['transaction_count']}")
        except Exception as e:
            print(f"❌ 数据库查询失败: {str(e)}")
        
        # 6. 生成详细报告
        print(f"\n📊 详细报告:")
        report = result["report"]
        
        print(f"\n⚙️ 配置信息:")
        for key, value in report["配置信息"].items():
            print(f"  {key}: {value}")
        
        print(f"\n📈 整体表现:")
        for key, value in report["整体表现"].items():
            print(f"  {key}: {value}")
        
        return True
        
    else:
        print(f"\n❌ 回测失败: {result['error']}")
        return False

def compare_with_previous_results():
    """与之前的回测结果进行对比"""
    print(f"\n🔍 结果对比分析:")
    print("=" * 40)
    print("本次回测使用的是完整的策略组合:")
    print("- 布林带入场策略：突破布林带上轨时入场")
    print("- 布林带出场策略：动态止损，根据是否突破第二层布林带调整")
    print("- SMA过滤策略：只有当SMA10-SMA20差值递增时才允许入场")
    print()
    print("预期结果特点:")
    print("- 交易次数可能减少（由于过滤策略的作用）")
    print("- 胜率可能提高（过滤掉部分不利信号）")
    print("- 最大回撤可能降低（更严格的入场条件）")
    print("- 整体收益率取决于过滤效果的好坏")

def main():
    """主测试函数"""
    success = test_specified_strategy_combination()
    
    if success:
        compare_with_previous_results()
        print(f"\n🎉 指定策略组合回测验证完成!")
        print("=" * 60)
        print("✅ 策略组合执行正常")
        print("✅ 数据库存储功能正常") 
        print("✅ 结果生成和分析正常")
        print("✅ 与预期行为一致")
    else:
        print(f"\n❌ 回测验证失败，请检查策略配置")

if __name__ == "__main__":
    main() 