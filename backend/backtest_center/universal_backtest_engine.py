import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import concurrent.futures
import os
import time

from backend.data_object_center.backtest_config import BacktestConfig, BacktestResult, BacktestSummary
from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager
from backend.backtest_center.backtest_core.backtest_system import BacktestSystem
from backend._utils import LogConfig
from backend.data_object_center.strategy_instance import StrategyInstance

logger = LogConfig.get_logger(__name__)

MIN_REQUIRED_ROWS = 50

class UniversalBacktestEngine:
    """通用回测引擎 - 支持灵活的策略组合配置"""
    
    def __init__(self, timezone_mode: str = "UTC-4"):
        """
        初始化通用回测引擎
        
        Args:
            timezone_mode: 时区模式，支持:
                - "UTC+8": 中国时间，日线以8:00为边界
                - "UTC-4": 美国东部时间，日线以0:00为边界
                - "UTC": 标准UTC时间
        """
        self.timezone_mode = timezone_mode
        self.data_manager = EnhancedKlineManager(timezone_mode=timezone_mode)
        self.results_cache: Dict[str, BacktestSummary] = {}
        logger.info(f"初始化通用回测引擎 (时区: {timezone_mode})")
        
    def run_backtest(self, config: BacktestConfig) -> Optional[BacktestSummary]:
        """运行回测"""
        try:
            logger.info("🚀 开始回测")
            
            # 根据backtest_period计算时间范围
            end_date = datetime(2025, 6, 1)  # 假设今天为2025年6月1日
            if config.backtest_period == '1m':
                start_date = datetime(2025, 5, 1)
            elif config.backtest_period == '3m':
                start_date = datetime(2025, 3, 1)
            elif config.backtest_period == '1y':
                start_date = datetime(2024, 6, 1)
            else:
                start_date = datetime(2025, 3, 1)  # 默认3个月
            
            # 转换为字符串格式
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            logger.info(f"回测时间范围: {start_date_str} 到 {end_date_str}")
            
            # 验证数据可用性
            available_data = {}
            for symbol in config.symbols:
                df = self.data_manager.get_kline_data(symbol, config.timeframe, start_date_str, end_date_str)
                if df is not None and len(df) >= MIN_REQUIRED_ROWS:
                    available_data[symbol] = df
                    logger.info(f"✅ {symbol}: {len(df)} 条数据可用，时间范围: {df.index.min()} 到 {df.index.max()}")
                else:
                    logger.warning(f"❌ {symbol}: 数据不足")
            
            if not available_data:
                logger.error("没有足够的可用数据")
                return None
            
            # 运行回测
            results = []
            for symbol, data in available_data.items():
                try:
                    result = self._run_single_symbol_backtest(
                        symbol=symbol,
                        data=data,
                        config=config
                    )
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"处理 {symbol} 时出错: {str(e)}")
                    continue
            
            if not results:
                logger.error("没有成功的回测结果")
                return None
            
            # 生成汇总报告
            summary = self._generate_summary(results, config)
            logger.info("✅ 回测完成")
            return summary
            
        except Exception as e:
            logger.error(f"回测执行出错: {str(e)}")
            return None
    
    def _run_single_symbol_backtest(self, symbol: str, data: pd.DataFrame, config: BacktestConfig) -> Optional[BacktestResult]:
        """运行单个交易对的回测"""
        try:
            import os
            logger.info(f"开始回测 {symbol}")
            
            # === 保存原始BTC kline数据 ===
            if symbol == 'BTC':
                tests_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
                os.makedirs(tests_dir, exist_ok=True)
                kline_file = os.path.join(tests_dir, f'btc_kline_data_{config.timeframe}_{config.backtest_period}.csv')
                data.to_csv(kline_file, index=True)
                logger.info(f"已保存BTC kline数据到: {kline_file}")
                logger.info(f"数据形状: {data.shape}")
                logger.info(f"数据列: {list(data.columns)}")
                logger.info(f"数据索引范围: {data.index.min()} 到 {data.index.max()}")
            
            # 确保数据类型正确
            for col in ['open', 'high', 'low', 'close', 'volume']:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # 确保datetime列是索引
            if 'datetime' in data.columns:
                data.set_index('datetime', inplace=True)
            data.index = pd.to_datetime(data.index)
            
            # 删除仅 OHLCV 缺失的行
            data = data.dropna(subset=['open', 'high', 'low', 'close', 'volume'])
            
            logger.info(f"{symbol}: rows after clean {len(data)}")
            
            # 按时间排序
            data = data.sort_index()
            
            # 计算技术指标（只计算必要的，避免过高窗口导致大量NaN 影响）
            data['sma10'] = data['close'].rolling(window=10).mean()
            data['sma20'] = data['close'].rolling(window=20).mean()
            data['sma50'] = data['close'].rolling(window=50).mean()
            # 仅在数据量充足时计算大周期
            if len(data) >= 200:
                data['sma100'] = data['close'].rolling(window=100).mean()
                data['sma200'] = data['close'].rolling(window=200).mean()
            
            # 删除NaN值
            data = data.dropna(subset=['sma20'])
            
            if len(data) < MIN_REQUIRED_ROWS:
                logger.warning(f"{symbol}: 数据不足 ({len(data)})")
                return None
            
            # 应用策略
            data = self._apply_entry_strategy(data, config.entry_strategy)
            
            # === 保存_apply_entry_strategy之后的数据 ===
            if symbol == 'BTC':
                tests_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
                after_entry_file = os.path.join(tests_dir, f'btc_after_entry_strategy_{config.entry_strategy}_{config.timeframe}_{config.backtest_period}.csv')
                data.to_csv(after_entry_file, index=True)
                logger.info(f"已保存应用入场策略后的BTC数据到: {after_entry_file}")
                logger.info(f"策略后数据形状: {data.shape}")
                logger.info(f"策略后数据列: {list(data.columns)}")
                if 'entry_sig' in data.columns:
                    entry_signals = data['entry_sig'].sum()
                    logger.info(f"入场信号总数: {entry_signals}")
                    signal_rows = data[data['entry_sig'] == 1]
                    if len(signal_rows) > 0:
                        logger.info(f"信号发生位置前5个: {signal_rows.index[:5].tolist()}")
                
            data = self._apply_exit_strategy(data, config.exit_strategy)
            entry_signals = data.get('entry_sig', pd.Series(0, index=data.index))
            exit_signals = data.get('sell_sig', pd.Series(0, index=data.index))
            
            if config.filter_strategy:
                filter_signals = self._apply_filter_strategy(data, config.filter_strategy)
            else:
                filter_signals = pd.Series(True, index=data.index)
            
            # 合并信号
            signals = pd.DataFrame({
                'entry': entry_signals,
                'exit': exit_signals,
                'filter': filter_signals
            })
            
            # 将信号列整合进data，符合 BacktestSystem 要求
            data['entry_sig'] = signals['entry'].astype(int)
            data['entry_price'] = np.where(data['entry_sig'] == 1, data['close'], 0)
            data['sell_sig'] = signals['exit'].astype(int)
            data['sell_price'] = np.where(data['sell_sig'] == 1, data['close'], data['close'])
            
            # 创建临时 StrategyInstance
            st = StrategyInstance()
            st.id = 0
            st.name = f"Temp_{symbol}"
            st.trade_pair = symbol
            st.side = 'long'
            st.entry_per_trans = 1000
            st.loss_per_trans = 1000
            st.time_frame = config.timeframe
            st.entry_st_code = config.entry_strategy
            st.exit_st_code = config.exit_strategy
            st.filter_st_code = config.filter_strategy or ''
            st.env = 'backtest'
            st.gmt_create = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.gmt_modified = st.gmt_create
            
            # 初始化回测系统并运行
            system = BacktestSystem(initial_cash=config.initial_cash,
                                     risk_percent=config.risk_percent,
                                     commission=config.commission)
            result_dict = system.run(data, st)
            
            if result_dict:
                logger.info(f"✅ {symbol} 回测完成")
                # 将旧格式结果转换为新的 BacktestResult 对象
                try:
                    config_key = config.generate_key()
                    backtest_result = self._convert_to_new_result_format(
                        old_result=result_dict,
                        config_key=config_key,
                        symbol=symbol,
                        df=data
                    )
                    return backtest_result
                except Exception as e:
                    logger.error(f"转换回测结果格式失败: {e}")
                    # 转换失败则放弃此结果，避免类型不一致
                    return None
            else:
                logger.warning(f"❌ {symbol} 回测失败")
                return None
            
        except Exception as e:
            logger.error(f"处理 {symbol} 时出错: {str(e)}")
            return None
    
    def _load_symbol_data(self, symbol: str, timeframe: str, start_date: Optional[str], end_date: Optional[str]) -> Optional[pd.DataFrame]:
        """加载交易对数据"""
        try:
            logger.info(f"加载 {symbol} 数据 - 时间框架: {timeframe}")
            df = self.data_manager.get_kline_data(symbol, timeframe, start_date, end_date)
            if df is None or len(df) == 0:
                logger.warning(f"无法获取 {symbol} 数据")
                return None
            return df
        except Exception as e:
            logger.error(f"加载 {symbol} 数据失败: {str(e)}")
            return None
            
    def _create_temp_strategy_instance(self, config: BacktestConfig, symbol: str) -> StrategyInstance:
        """创建临时策略实例"""
        logger.info(f"创建临时策略实例 - {symbol}")
        return StrategyInstance(
            id=0,
            name=f"Temp_{symbol}",
            trade_pair=symbol,
            entry_st_code=config.entry_strategy,
            exit_st_code=config.exit_strategy,
            filter_st_code=config.filter_strategy,
            time_frame=config.timeframe
        )
        
    def _convert_to_new_result_format(self, old_result: dict, config_key: str, symbol: str, df: pd.DataFrame) -> BacktestResult:
        """将旧的回测结果格式转换为新格式"""
        logger.info(f"转换回测结果格式 - {symbol}")
        
        # 计算信号执行率
        total_entry_signals = int(df['entry_sig'].sum()) if 'entry_sig' in df.columns else 0
        total_trades = old_result.get('total_trades', 0)
        signal_execution_rate = (total_trades / total_entry_signals * 100) if total_entry_signals > 0 else 0
        
        # 计算回测天数
        start_date = df.index.min()
        end_date = df.index.max()
        duration_days = (end_date - start_date).days
        
        logger.info(f"回测统计 - {symbol}")
        logger.info(f"总信号数: {total_entry_signals}")
        logger.info(f"总交易数: {total_trades}")
        logger.info(f"信号执行率: {signal_execution_rate:.1f}%")
        logger.info(f"回测天数: {duration_days}")
        
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
    
    def _generate_summary(self, individual_results: List[BacktestResult], config: BacktestConfig) -> BacktestSummary:
        """生成汇总结果"""
        logger.info("生成回测汇总结果")
        
        if not individual_results:
            logger.warning("没有有效回测结果")
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
        
        logger.info("回测汇总统计")
        logger.info(f"总交易对数量: {len(individual_results)}")
        logger.info(f"平均收益率: {np.mean(returns):.2%}")
        logger.info(f"最佳交易对: {best_result.symbol} ({best_result.total_return:.2%})")
        logger.info(f"最差交易对: {worst_result.symbol} ({worst_result.total_return:.2%})")
        logger.info(f"平均胜率: {np.mean(win_rates):.1f}%")
        logger.info(f"平均夏普比率: {np.mean(sharpe_ratios) if sharpe_ratios else 0:.2f}")
        
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

    def _apply_entry_strategy(self, df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
        """执行入场策略, 返回带 entry_sig 列的 df"""
        func = registry.get_strategy(strategy_name)
        if func is None:
            logger.warning(f"入场策略 {strategy_name} 未找到, 默认无信号")
            df['entry_sig'] = 0
            return df
        try:
            return func(df.copy(), None)  # backtest 版策略第二参数传 None
        except Exception as e:
            logger.error(f"执行入场策略 {strategy_name} 出错: {e}")
            df['entry_sig'] = 0
            return df

    def _apply_exit_strategy(self, df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
        """执行离场策略, 返回带 sell_sig 列的 df"""
        func = registry.get_strategy(strategy_name)
        if func is None:
            logger.warning(f"离场策略 {strategy_name} 未找到, 默认无信号")
            df['sell_sig'] = 0
            return df
        try:
            return func(df.copy(), None)
        except Exception as e:
            logger.error(f"执行离场策略 {strategy_name} 出错: {e}")
            df['sell_sig'] = 0
            return df

    def _apply_filter_strategy(self, df: pd.DataFrame, strategy_name: str) -> pd.Series:
        """过滤策略, 返回 bool Series"""
        func = registry.get_strategy(strategy_name)
        if func is None:
            logger.warning(f"过滤策略 {strategy_name} 未找到, 默认全部通过")
            return pd.Series(True, index=df.index)
        try:
            df2 = func(df.copy(), None)
            return df2.get('filter_sig', pd.Series(True, index=df.index))
        except Exception as e:
            logger.error(f"执行过滤策略 {strategy_name} 出错: {e}")
            return pd.Series(True, index=df.index)


# 全局实例
universal_engine = UniversalBacktestEngine() 