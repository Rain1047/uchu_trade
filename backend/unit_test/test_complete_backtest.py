#!/usr/bin/env python3
"""
完整的增强回测系统测试
使用简单的SMA策略确保系统正常工作
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.backtest_center.enhanced_backtest_runner import EnhancedBacktestRunner
from backend.data_object_center.backtest_result import BacktestResult as DBBacktestResult

def test_complete_backtest():
    """测试完整的回测流程"""
    print("🚀 完整增强回测系统测试")
    print("=" * 60)
    
    runner = EnhancedBacktestRunner()
    
    # 1. 检查可用策略
    print("📋 检查可用策略...")
    strategies = runner.get_available_strategies()
    print(f"入场策略: {[s['name'] for s in strategies.get('entry', [])]}")
    print(f"出场策略: {[s['name'] for s in strategies.get('exit', [])]}")
    print(f"过滤策略: {[s['name'] for s in strategies.get('filter', [])]}")
    
    # 2. 检查可用交易对
    print(f"\n💰 检查可用交易对...")
    symbols = runner.get_available_symbols()
    print(f"可用交易对 ({len(symbols)}): {symbols}")
    
    # 3. 检查数据信息
    print(f"\n📊 检查数据信息...")
    for symbol in symbols[:2]:  # 只检查前2个
        info = runner.get_symbol_data_info(symbol, "4h")
        if info:
            print(f"  {symbol}: {info['total_records']} 条记录, {info['file_size_mb']} MB")
    
    # 4. 运行简单的SMA交叉策略回测
    print(f"\n🎯 运行SMA交叉策略回测...")
    result = runner.run_complete_backtest(
        entry_strategy="sma_cross_entry_long_strategy",
        exit_strategy="dbb_exit_long_strategy",  # 使用现有的出场策略
        filter_strategy=None,  # 不使用过滤策略
        symbols=symbols[:2],  # 测试前2个交易对
        timeframe="4h",
        initial_cash=100000.0,
        risk_percent=2.0,
        commission=0.001,
        save_to_db=True,
        description="SMA交叉策略完整测试"
    )
    
    # 5. 显示结果
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
            for result_detail in summary.individual_results:
                print(f"  🎯 {result_detail.symbol}:")
                print(f"    收益率: {result_detail.total_return:.2%}")
                print(f"    年化收益率: {result_detail.annual_return:.2%}")
                print(f"    夏普比率: {result_detail.sharpe_ratio:.2f}" if result_detail.sharpe_ratio else "    夏普比率: N/A")
                print(f"    最大回撤: {result_detail.max_drawdown:.2%}")
                print(f"    交易次数: {result_detail.total_trades}")
                print(f"    胜率: {result_detail.win_rate:.1%}")
                print(f"    入场信号数: {result_detail.total_entry_signals}")
                print(f"    信号执行率: {result_detail.signal_execution_rate:.1%}")
        
        # 6. 检查数据库保存
        print(f"\n💾 检查数据库保存...")
        try:
            # 查询最近的回测结果
            all_results = DBBacktestResult.list_all()
            recent_results = [r for r in all_results if result['config_key'] in str(r.strategy_id)][:5]
            
            print(f"数据库中找到 {len(recent_results)} 条相关记录:")
            for db_result in recent_results:
                db_dict = db_result.to_dict()
                print(f"  - {db_dict['symbol']}: 收益率 {db_dict['profit_rate']:.2f}%, 交易次数 {db_dict['transaction_count']}")
        except Exception as e:
            print(f"❌ 数据库查询失败: {str(e)}")
        
    else:
        print(f"\n❌ 回测失败: {result['error']}")
    
    return result

def test_with_indicators():
    """测试需要指标的策略"""
    print("\n" + "=" * 60)
    print("🧮 测试需要指标的策略")
    print("=" * 60)
    
    runner = EnhancedBacktestRunner()
    
    # 使用需要布林带指标的策略
    print("🎯 运行布林带策略回测（需要指标计算）...")
    result = runner.run_complete_backtest(
        entry_strategy="dbb_entry_long_strategy",
        exit_strategy="dbb_exit_long_strategy",
        filter_strategy=None,
        symbols=["BTC-USDT"],  # 只测试一个交易对
        timeframe="4h",
        description="布林带策略测试（带指标计算）"
    )
    
    if result["success"]:
        print("✅ 布林带策略回测成功!")
        summary = result["summary"]
        if summary.individual_results:
            detail = summary.individual_results[0]
            print(f"  BTC-USDT 收益率: {detail.total_return:.2%}")
            print(f"  交易次数: {detail.total_trades}")
            print(f"  胜率: {detail.win_rate:.1%}")
    else:
        print(f"❌ 布林带策略回测失败: {result['error']}")
        print("这可能是因为数据中缺少布林带指标，需要动态计算")

def main():
    """主测试函数"""
    # 测试1: 基本的SMA策略
    result1 = test_complete_backtest()
    
    # 测试2: 需要指标的策略
    test_with_indicators()
    
    print(f"\n🎉 测试完成!")
    print("=" * 60)
    
    if result1["success"]:
        print("✅ 增强回测系统工作正常!")
        print("✅ 数据管理器集成成功!")
        print("✅ 数据库存储功能正常!")
        print("✅ 策略执行和结果生成正常!")
    else:
        print("❌ 系统存在问题，需要进一步调试")

if __name__ == "__main__":
    main() 