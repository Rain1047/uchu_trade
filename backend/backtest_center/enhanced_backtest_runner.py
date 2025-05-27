#!/usr/bin/env python3
"""
增强的回测运行器
- 集成新的数据管理器
- 支持数据库存储
- 完整的回测流程
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager, CommonIndicators
from backend.data_object_center.backtest_config import BacktestConfig
from backend.data_object_center.backtest_result import BacktestResult as DBBacktestResult
from backend.backtest_center.universal_backtest_engine import universal_engine
from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)


class EnhancedBacktestRunner:
    """增强的回测运行器"""
    
    def __init__(self):
        self.data_manager = EnhancedKlineManager()
        self.logger = logging.getLogger(__name__)
        
    def run_complete_backtest(self, 
                            entry_strategy: str,
                            exit_strategy: str,
                            filter_strategy: Optional[str] = None,
                            symbols: List[str] = None,
                            timeframe: str = "4h",
                            initial_cash: float = 100000.0,
                            risk_percent: float = 2.0,
                            commission: float = 0.001,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            save_to_db: bool = True,
                            description: str = "增强回测") -> Dict:
        """
        运行完整的回测流程
        
        Args:
            entry_strategy: 入场策略名称
            exit_strategy: 出场策略名称
            filter_strategy: 过滤策略名称（可选）
            symbols: 交易对列表
            timeframe: 时间框架
            initial_cash: 初始资金
            risk_percent: 风险百分比
            commission: 手续费
            start_date: 开始日期
            end_date: 结束日期
            save_to_db: 是否保存到数据库
            description: 描述
            
        Returns:
            Dict: 回测结果汇总
        """
        
        self.logger.info("🚀 开始增强回测流程")
        
        # 1. 验证策略是否存在
        if not self._validate_strategies(entry_strategy, exit_strategy, filter_strategy):
            return {"success": False, "error": "策略验证失败"}
        
        # 2. 获取可用交易对（如果未指定）
        if symbols is None:
            symbols = self._get_default_symbols()
        
        # 3. 验证数据可用性
        valid_symbols = self._validate_symbols_data(symbols, timeframe)
        if not valid_symbols:
            return {"success": False, "error": "没有可用的交易对数据"}
        
        self.logger.info(f"📊 将测试 {len(valid_symbols)} 个交易对: {valid_symbols}")
        
        # 4. 创建回测配置
        config = BacktestConfig(
            entry_strategy=entry_strategy,
            exit_strategy=exit_strategy,
            filter_strategy=filter_strategy,
            symbols=valid_symbols,
            timeframe=timeframe,
            initial_cash=initial_cash,
            risk_percent=risk_percent,
            commission=commission,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        
        self.logger.info(f"⚙️ 回测配置: {config.get_display_name()}")
        self.logger.info(f"🔑 配置键: {config.generate_key()}")
        
        # 5. 运行回测
        try:
            summary = universal_engine.run_backtest(config)
            
            # 6. 保存到数据库（如果需要）
            if save_to_db and summary.individual_results:
                self._save_results_to_database(summary, config)
            
            # 7. 生成报告
            report = self._generate_report(summary, config)
            
            self.logger.info("✅ 回测完成!")
            return {
                "success": True,
                "config_key": config.generate_key(),
                "summary": summary,
                "report": report,
                "config": config
            }
            
        except Exception as e:
            self.logger.error(f"❌ 回测失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _validate_strategies(self, entry_strategy: str, exit_strategy: str, filter_strategy: Optional[str]) -> bool:
        """验证策略是否存在"""
        available_strategies = universal_engine.get_available_strategies()
        
        # 检查入场策略
        entry_names = [s['name'] for s in available_strategies.get('entry', [])]
        if entry_strategy not in entry_names:
            self.logger.error(f"入场策略 '{entry_strategy}' 不存在。可用策略: {entry_names}")
            return False
        
        # 检查出场策略
        exit_names = [s['name'] for s in available_strategies.get('exit', [])]
        if exit_strategy not in exit_names:
            self.logger.error(f"出场策略 '{exit_strategy}' 不存在。可用策略: {exit_names}")
            return False
        
        # 检查过滤策略（如果指定）
        if filter_strategy:
            filter_names = [s['name'] for s in available_strategies.get('filter', [])]
            if filter_strategy not in filter_names:
                self.logger.error(f"过滤策略 '{filter_strategy}' 不存在。可用策略: {filter_names}")
                return False
        
        return True
    
    def _get_default_symbols(self) -> List[str]:
        """获取默认的交易对列表"""
        available_symbols = universal_engine.get_available_symbols()
        # 返回前3个交易对作为默认测试
        return available_symbols[:3] if len(available_symbols) >= 3 else available_symbols
    
    def _validate_symbols_data(self, symbols: List[str], timeframe: str) -> List[str]:
        """验证交易对数据可用性"""
        valid_symbols = []
        
        for symbol in symbols:
            # 获取基础货币
            base_symbol = symbol.split('-')[0] if '-' in symbol else symbol.replace('USDT', '')
            
            # 检查数据是否存在
            try:
                df = self.data_manager.load_raw_data(base_symbol, timeframe)
                if df is not None and len(df) >= 100:  # 至少需要100条数据
                    valid_symbols.append(symbol)
                    self.logger.info(f"✅ {symbol}: {len(df)} 条数据可用")
                else:
                    self.logger.warning(f"❌ {symbol}: 数据不足或不存在")
            except Exception as e:
                self.logger.warning(f"❌ {symbol}: 数据加载失败 - {str(e)}")
        
        return valid_symbols
    
    def _save_results_to_database(self, summary, config: BacktestConfig):
        """保存结果到数据库"""
        self.logger.info("💾 保存结果到数据库...")
        
        try:
            for result in summary.individual_results:
                # 生成数据库记录的键
                db_key = f"{result.symbol}_{config.generate_key()}_{datetime.now().strftime('%Y%m%d%H%M')}"
                
                # 构造数据库记录
                db_data = {
                    'back_test_result_key': db_key,
                    'symbol': result.symbol,
                    'strategy_id': config.generate_key(),
                    'strategy_name': config.get_display_name(),
                    'test_finished_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'buy_signal_count': result.total_entry_signals,
                    'sell_signal_count': result.total_sell_signals,
                    'transaction_count': result.total_trades,
                    'profit_count': result.winning_trades,
                    'loss_count': result.losing_trades,
                    'profit_total_count': result.total_return,
                    'profit_average': result.total_return / result.total_trades if result.total_trades > 0 else 0,
                    'profit_rate': result.total_return * 100,  # 转换为百分比
                }
                
                # 保存到数据库
                from backend.data_object_center.backtest_result import BacktestResult as DBBacktestResult
                DBBacktestResult.insert_or_update(db_data)
                self.logger.info(f"✅ 已保存 {result.symbol} 的结果到数据库")
                
        except Exception as e:
            self.logger.error(f"❌ 保存到数据库失败: {str(e)}")
    
    def _generate_report(self, summary, config: BacktestConfig) -> Dict:
        """生成详细报告"""
        report = {
            "配置信息": {
                "策略组合": f"{config.entry_strategy} + {config.exit_strategy}" + 
                          (f" + {config.filter_strategy}" if config.filter_strategy else ""),
                "交易对": config.symbols,
                "时间框架": config.timeframe,
                "初始资金": f"${config.initial_cash:,.2f}",
                "风险百分比": f"{config.risk_percent}%",
                "手续费": f"{config.commission * 100}%",
                "测试时间": config.created_at
            },
            "整体表现": {
                "测试交易对数量": summary.total_symbols,
                "平均收益率": f"{summary.avg_return:.2%}",
                "最佳交易对": f"{summary.best_symbol} ({summary.best_return:.2%})" if summary.best_symbol else "无",
                "最差交易对": f"{summary.worst_symbol} ({summary.worst_return:.2%})" if summary.worst_symbol else "无",
                "总交易次数": summary.total_trades_all,
                "平均胜率": f"{min(summary.avg_win_rate / 100 if summary.avg_win_rate > 1 else summary.avg_win_rate, 1.0):.1%}",
                "平均夏普比率": f"{summary.avg_sharpe:.2f}" if summary.avg_sharpe and summary.avg_sharpe != 0 else "N/A"
            },
            "详细结果": []
        }
        
        # 添加每个交易对的详细结果
        for result in summary.individual_results:
            # 安全处理最大回撤 - 确保在合理范围内
            max_drawdown = result.max_drawdown
            if max_drawdown > 1:  # 如果大于1，假设已经是百分比形式，需要除以100
                max_drawdown = max_drawdown / 100
            max_drawdown = min(max_drawdown, 1.0)  # 最大回撤不能超过100%
            
            # 安全处理胜率 - 确保在0-100%范围内
            win_rate = result.win_rate
            if win_rate > 1:  # 如果大于1，假设已经是百分比形式，需要除以100
                win_rate = win_rate / 100
            win_rate = min(win_rate, 1.0)  # 胜率不能超过100%
            
            # 安全处理信号执行率
            signal_execution_rate = result.signal_execution_rate
            if signal_execution_rate > 1:  # 如果大于1，假设已经是百分比形式，需要除以100
                signal_execution_rate = signal_execution_rate / 100
            signal_execution_rate = min(signal_execution_rate, 1.0)  # 执行率不能超过100%
            
            detail = {
                "交易对": result.symbol,
                "收益率": f"{result.total_return:.2%}",
                "年化收益率": f"{result.annual_return:.2%}",
                "夏普比率": f"{result.sharpe_ratio:.2f}" if result.sharpe_ratio and result.sharpe_ratio != 0 else "N/A",
                "最大回撤": f"{max_drawdown:.2%}",
                "交易次数": result.total_trades,
                "胜率": f"{win_rate:.1%}",
                "入场信号数": result.total_entry_signals,
                "信号执行率": f"{signal_execution_rate:.1%}",
                "测试天数": result.duration_days
            }
            report["详细结果"].append(detail)
        
        return report
    
    def get_available_strategies(self) -> Dict:
        """获取可用策略"""
        return universal_engine.get_available_strategies()
    
    def get_available_symbols(self) -> List[str]:
        """获取可用交易对"""
        return universal_engine.get_available_symbols()
    
    def get_symbol_data_info(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """获取交易对数据信息"""
        base_symbol = symbol.split('-')[0] if '-' in symbol else symbol.replace('USDT', '')
        return self.data_manager.get_data_info(base_symbol, timeframe)


def run_demo_backtest():
    """运行演示回测"""
    print("🚀 增强回测系统演示")
    print("=" * 60)
    
    runner = EnhancedBacktestRunner()
    
    # 获取可用策略
    strategies = runner.get_available_strategies()
    print("📋 可用策略:")
    for strategy_type, strategy_list in strategies.items():
        print(f"  {strategy_type.upper()}:")
        for strategy in strategy_list:
            print(f"    - {strategy['name']}: {strategy['desc']}")
    
    # 获取可用交易对
    symbols = runner.get_available_symbols()
    print(f"\n💰 可用交易对 ({len(symbols)}): {symbols}")
    
    # 运行回测
    print(f"\n🎯 开始回测...")
    result = runner.run_complete_backtest(
        entry_strategy="dbb_entry_long_strategy",
        exit_strategy="dbb_exit_long_strategy",
        filter_strategy="sma_perfect_order_filter_strategy",
        symbols=symbols[:2],  # 测试前2个交易对
        timeframe="4h",
        description="增强回测系统演示"
    )
    
    if result["success"]:
        print("\n✅ 回测成功完成!")
        print(f"配置键: {result['config_key']}")
        
        # 打印报告
        report = result["report"]
        print(f"\n📊 回测报告:")
        print(f"=" * 40)
        
        print(f"\n⚙️ 配置信息:")
        for key, value in report["配置信息"].items():
            print(f"  {key}: {value}")
        
        print(f"\n📈 整体表现:")
        for key, value in report["整体表现"].items():
            print(f"  {key}: {value}")
        
        print(f"\n📋 详细结果:")
        for detail in report["详细结果"]:
            print(f"\n  🎯 {detail['交易对']}:")
            for key, value in detail.items():
                if key != "交易对":
                    print(f"    {key}: {value}")
    else:
        print(f"\n❌ 回测失败: {result['error']}")


if __name__ == "__main__":
    run_demo_backtest() 