import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import concurrent.futures
import os

from backend.data_object_center.backtest_config import BacktestConfig, BacktestResult, BacktestSummary
from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager
from backend.backtest_center.backtest_core.backtest_system import BacktestSystem
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)


class UniversalBacktestEngine:
    """通用回测引擎 - 支持灵活的策略组合配置"""
    
    def __init__(self):
        self.data_manager = EnhancedKlineManager()
        self.results_cache: Dict[str, BacktestSummary] = {}
        
    def run_backtest(self, config: BacktestConfig, save_results: bool = True) -> BacktestSummary:
        """
        运行回测
        
        Args:
            config: 回测配置
            save_results: 是否保存结果到缓存
            
        Returns:
            BacktestSummary: 回测汇总结果
        """
        config_key = config.generate_key()
        
        # 检查缓存
        if config_key in self.results_cache:
            logger.info(f"从缓存中获取回测结果: {config_key}")
            return self.results_cache[config_key]
        
        logger.info(f"开始回测: {config.get_display_name()}")
        logger.info(f"配置键: {config_key}")
        
        # 并行处理多个交易对
        individual_results = []
        
        if len(config.symbols) == 1:
            # 单个交易对，直接运行
            result = self._run_single_symbol_backtest(config, config.symbols[0])
            if result:
                individual_results.append(result)
        else:
            # 多个交易对，并行处理
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_symbol = {
                    executor.submit(self._run_single_symbol_backtest, config, symbol): symbol 
                    for symbol in config.symbols
                }
                
                for future in concurrent.futures.as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        if result:
                            individual_results.append(result)
                            logger.info(f"完成 {symbol} 回测")
                    except Exception as e:
                        logger.error(f"回测 {symbol} 失败: {str(e)}")
        
        # 生成汇总结果
        summary = self._generate_summary(config, individual_results)
        
        if save_results:
            self.results_cache[config_key] = summary
            
        return summary
    
    def _run_single_symbol_backtest(self, config: BacktestConfig, symbol: str) -> Optional[BacktestResult]:
        """运行单个交易对的回测"""
        try:
            # 1. 加载数据
            df = self._load_symbol_data(symbol, config.timeframe, config.start_date, config.end_date)
            if df is None or len(df) < 100:  # 数据不足
                logger.warning(f"交易对 {symbol} 数据不足，跳过回测")
                return None
            
            # 2. 应用策略生成信号
            df = self._apply_strategies(df, config)
            
            # 3. 运行回测
            backtest_system = BacktestSystem(
                initial_cash=config.initial_cash,
                risk_percent=config.risk_percent,
                commission=config.commission
            )
            
            # 创建临时策略实例对象（兼容现有系统）
            temp_st = self._create_temp_strategy_instance(config, symbol)
            
            backtest_results = backtest_system.run(df, temp_st, plot=False)
            
            # 4. 转换为新的结果格式
            result = self._convert_to_new_result_format(
                backtest_results, config.generate_key(), symbol, df
            )
            
            return result
            
        except Exception as e:
            logger.error(f"回测 {symbol} 时发生错误: {str(e)}")
            return None
    
    def _load_symbol_data(self, symbol: str, timeframe: str, start_date: Optional[str], end_date: Optional[str]) -> Optional[pd.DataFrame]:
        """加载交易对数据"""
        try:
            # 获取基础货币（去掉交易对后缀）
            base_symbol = symbol.split('-')[0] if '-' in symbol else symbol.replace('USDT', '')
            
            # 使用新的数据管理器加载数据，并计算常用指标
            from backend.data_center.kline_data.enhanced_kline_manager import CommonIndicators
            
            # 先加载原始数据
            df = self.data_manager.load_raw_data(base_symbol, timeframe, start_date, end_date)
            
            if df is None:
                logger.warning(f"无法加载 {symbol} 的数据")
                return None
            
            # 重置索引，将datetime作为普通列
            df = df.reset_index()
            
            # 手动计算常用指标
            df['SMA10'] = df['close'].rolling(window=10).mean()
            df['sma20'] = df['close'].rolling(window=20).mean()
            df['SMA30'] = df['close'].rolling(window=30).mean()
            
            # 计算布林带
            df['middle_band'] = df['sma20']  # 中轨就是SMA20
            rolling_std = df['close'].rolling(window=20).std()
            df['upper_band1'] = df['middle_band'] + 2 * rolling_std
            df['lower_band1'] = df['middle_band'] - 2 * rolling_std
            df['upper_band2'] = df['middle_band'] + 3 * rolling_std
            df['lower_band2'] = df['middle_band'] - 3 * rolling_std
            
            logger.info(f"加载 {symbol} 数据: {len(df)} 条记录，包含指标: {[col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume', 'datetime']]}")
            return df
            
        except Exception as e:
            logger.error(f"加载 {symbol} 数据失败: {str(e)}")
            return None
    
    def _apply_strategies(self, df: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
        """应用策略生成信号"""
        try:
            # 应用入场策略 - 传入None作为stIns参数，触发回测模式
            entry_strategy = registry.get_strategy(config.entry_strategy)
            df = entry_strategy(df, None)  # 传入None触发回测模式
            
            # 应用出场策略 - 传入None作为stIns参数，触发回测模式
            exit_strategy = registry.get_strategy(config.exit_strategy)
            df = exit_strategy(df, None)  # 传入None触发回测模式
            
            # 应用过滤策略（如果有）
            if config.filter_strategy:
                filter_strategy = registry.get_strategy(config.filter_strategy)
                df = filter_strategy(df, None)  # 传入None作为stIns参数，触发回测模式
                
                # 过滤策略可能会修改入场信号
                if 'filtered_entry_sig' in df.columns:
                    df['entry_sig'] = df['filtered_entry_sig']
            
            # 确保必要的列存在
            required_columns = ['entry_sig', 'entry_price', 'sell_sig', 'sell_price']
            for col in required_columns:
                if col not in df.columns:
                    if 'entry' in col:
                        df[col] = 0
                    else:  # sell相关
                        df[col] = df['close']  # 默认使用收盘价
            
            return df
            
        except Exception as e:
            logger.error(f"应用策略失败: {str(e)}")
            raise
    
    def _create_temp_strategy_instance(self, config: BacktestConfig, symbol: str):
        """创建临时策略实例对象（兼容现有回测系统）"""
        class TempStrategyInstance:
            def __init__(self, config: BacktestConfig, symbol: str):
                self.id = f"temp_{config.generate_key()}_{symbol}"
                self.trade_pair = symbol
                self.time_frame = config.timeframe
                self.entry_st_code = config.entry_strategy
                self.exit_st_code = config.exit_strategy
                self.filter_st_code = config.filter_strategy
        
        return TempStrategyInstance(config, symbol)
    
    def _convert_to_new_result_format(self, old_result: dict, config_key: str, symbol: str, df: pd.DataFrame) -> BacktestResult:
        """将旧的回测结果格式转换为新格式"""
        
        # 计算信号执行率
        total_entry_signals = int(df['entry_sig'].sum()) if 'entry_sig' in df.columns else 0
        total_trades = old_result.get('total_trades', 0)
        signal_execution_rate = (total_trades / total_entry_signals * 100) if total_entry_signals > 0 else 0
        
        # 计算回测天数
        start_date = df['datetime'].min()
        end_date = df['datetime'].max()
        duration_days = (end_date - start_date).days
        
        return BacktestResult(
            config_key=config_key,
            symbol=symbol,
            initial_value=old_result.get('initial_value', 0),
            final_value=old_result.get('final_value', 0),
            total_return=old_result.get('total_return', 0),
            annual_return=old_result.get('annual_return', 0),
            sharpe_ratio=old_result.get('sharpe_ratio', 0),
            max_drawdown=old_result.get('max_drawdown', 0),
            max_drawdown_amount=old_result.get('max_drawdown_amount', 0),
            total_trades=total_trades,
            winning_trades=old_result.get('winning_trades', 0),
            losing_trades=old_result.get('losing_trades', 0),
            win_rate=old_result.get('win_rate', 0),
            avg_win=old_result.get('avg_win', 0),
            avg_loss=old_result.get('avg_loss', 0),
            total_entry_signals=total_entry_signals,
            total_sell_signals=int(df['sell_sig'].sum()) if 'sell_sig' in df.columns else 0,
            signal_execution_rate=signal_execution_rate,
            backtest_date=datetime.now().isoformat(),
            duration_days=duration_days
        )
    
    def _generate_summary(self, config: BacktestConfig, individual_results: List[BacktestResult]) -> BacktestSummary:
        """生成汇总结果"""
        if not individual_results:
            # 如果没有有效结果，返回空汇总
            return BacktestSummary(
                config_key=config.generate_key(),
                config=config,
                total_symbols=0,
                avg_return=0,
                best_symbol="",
                worst_symbol="",
                best_return=0,
                worst_return=0,
                total_trades_all=0,
                avg_win_rate=0,
                avg_sharpe=0,
                individual_results=[],
                created_at=datetime.now().isoformat()
            )
        
        # 计算汇总统计
        returns = [r.total_return for r in individual_results]
        win_rates = [r.win_rate for r in individual_results]
        sharpe_ratios = [r.sharpe_ratio for r in individual_results if r.sharpe_ratio is not None]
        
        best_result = max(individual_results, key=lambda x: x.total_return)
        worst_result = min(individual_results, key=lambda x: x.total_return)
        
        return BacktestSummary(
            config_key=config.generate_key(),
            config=config,
            total_symbols=len(individual_results),
            avg_return=np.mean(returns),
            best_symbol=best_result.symbol,
            worst_symbol=worst_result.symbol,
            best_return=best_result.total_return,
            worst_return=worst_result.total_return,
            total_trades_all=sum(r.total_trades for r in individual_results),
            avg_win_rate=np.mean(win_rates),
            avg_sharpe=np.mean(sharpe_ratios) if sharpe_ratios else 0,
            individual_results=individual_results,
            created_at=datetime.now().isoformat()
        )
    
    def get_available_strategies(self) -> Dict[str, List[str]]:
        """获取可用的策略列表"""
        strategies = registry.list_strategies()
        
        result = {
            'entry': [],
            'exit': [],
            'filter': []
        }
        
        for strategy in strategies:
            strategy_type = strategy.get('type', 'unknown')
            if strategy_type in result:
                result[strategy_type].append({
                    'name': strategy['name'],
                    'desc': strategy.get('desc', ''),
                    'side': strategy.get('side', '')
                })
        
        return result
    
    def get_available_symbols(self) -> List[str]:
        """获取可用的交易对列表"""
        try:
            # 使用新的数据管理器获取可用交易对
            base_symbols = self.data_manager.get_available_symbols()
            # 转换为交易对格式
            return [f"{symbol}-USDT" for symbol in base_symbols]
        except Exception as e:
            logger.error(f"获取可用交易对失败: {str(e)}")
            return []
    
    def get_cached_results(self) -> List[BacktestSummary]:
        """获取缓存的回测结果"""
        return list(self.results_cache.values())
    
    def clear_cache(self):
        """清空结果缓存"""
        self.results_cache.clear()
        logger.info("回测结果缓存已清空")


# 全局实例
universal_engine = UniversalBacktestEngine() 