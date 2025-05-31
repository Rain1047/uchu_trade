#!/usr/bin/env python3
"""
增强的K线数据管理器
- 统一时间间隔格式
- 按需计算指标
- 智能缓存机制
- 灵活的数据获取接口
"""

import os
import logging
import hashlib
from typing import Optional, Dict, List, Union, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from functools import lru_cache

# 技术指标库
try:
    import talib as ta
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available, some indicators will be disabled")


@dataclass
class TimeFrameConfig:
    """时间框架配置"""
    standard_name: str  # 标准名称，如 '1h', '4h', '1d'
    file_suffix: str    # 文件后缀，如 '1H', '4H', '1D'
    tv_interval: str    # TradingView间隔，如 '1h', '4h', '1D'
    minutes: int        # 对应的分钟数
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, 'TimeFrameConfig']:
        """获取所有支持的时间框架配置"""
        return {
            '1m': cls('1m', '1M', '1m', 1),
            '5m': cls('5m', '5M', '5m', 5),
            '15m': cls('15m', '15M', '15m', 15),
            '30m': cls('30m', '30M', '30m', 30),
            '1h': cls('1h', '1H', '1h', 60),
            '2h': cls('2h', '2H', '2h', 120),
            '4h': cls('4h', '4H', '4h', 240),
            '6h': cls('6h', '6H', '6h', 360),
            '12h': cls('12h', '12H', '12h', 720),
            '1d': cls('1d', '1D', '1D', 1440),
            '3d': cls('3d', '3D', '3D', 4320),
            '1w': cls('1w', '1W', '1W', 10080),
        }


@dataclass
class IndicatorRequest:
    """指标请求配置"""
    name: str                           # 指标名称
    params: Dict = field(default_factory=dict)  # 指标参数
    cache_key: Optional[str] = None     # 缓存键
    
    def __post_init__(self):
        if self.cache_key is None:
            # 生成缓存键
            params_str = str(sorted(self.params.items()))
            self.cache_key = hashlib.md5(f"{self.name}_{params_str}".encode()).hexdigest()[:8]


class IndicatorCalculator:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 20, source: str = 'close') -> pd.Series:
        """简单移动平均"""
        if TALIB_AVAILABLE:
            return ta.SMA(df[source].values, timeperiod=period)
        else:
            return df[source].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20, source: str = 'close') -> pd.Series:
        """指数移动平均"""
        if TALIB_AVAILABLE:
            return ta.EMA(df[source].values, timeperiod=period)
        else:
            return df[source].ewm(span=period).mean()
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0, source: str = 'close') -> Tuple[pd.Series, pd.Series, pd.Series]:
        """布林带"""
        if TALIB_AVAILABLE:
            upper, middle, lower = ta.BBANDS(df[source].values, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
            return pd.Series(upper), pd.Series(middle), pd.Series(lower)
        else:
            sma = df[source].rolling(window=period).mean()
            std = df[source].rolling(window=period).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return upper, sma, lower
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, source: str = 'close') -> pd.Series:
        """相对强弱指数"""
        if TALIB_AVAILABLE:
            return ta.RSI(df[source].values, timeperiod=period)
        else:
            delta = df[source].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, source: str = 'close') -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD指标"""
        if TALIB_AVAILABLE:
            macd, signal_line, histogram = ta.MACD(df[source].values, fastperiod=fast, slowperiod=slow, signalperiod=signal)
            return pd.Series(macd), pd.Series(signal_line), pd.Series(histogram)
        else:
            ema_fast = df[source].ewm(span=fast).mean()
            ema_slow = df[source].ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            return macd, signal_line, histogram
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """平均趋向指数"""
        if TALIB_AVAILABLE:
            return ta.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        else:
            # 简化版ADX计算
            high = df['high']
            low = df['low']
            close = df['close']
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            minus_dm = minus_dm.abs()
            
            tr1 = pd.DataFrame(high - low).rename(columns={'high': 'tr'})
            tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns={'high': 'tr'})
            tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns={'low': 'tr'})
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            atr = tr.rolling(window=period).mean()
            plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
            
            dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
            adx = dx.rolling(window=period).mean()
            
            return adx
    
    @classmethod
    def get_available_indicators(cls) -> Dict[str, callable]:
        """获取所有可用的指标计算函数"""
        return {
            'sma': cls.calculate_sma,
            'ema': cls.calculate_ema,
            'bollinger_bands': cls.calculate_bollinger_bands,
            'rsi': cls.calculate_rsi,
            'macd': cls.calculate_macd,
            'adx': cls.calculate_adx,
        }


class EnhancedKlineManager:
    """增强的K线数据管理器"""
    
    def __init__(self, data_dir: Optional[str] = None, timezone_mode: str = "UTC-4"):
        """
        初始化增强的K线数据管理器
        
        Args:
            data_dir: 数据目录路径
            timezone_mode: 时区模式，支持:
                - "UTC+8": 中国时间，日线以8:00为边界
                - "UTC-4": 美国东部时间，日线以0:00为边界
                - "UTC": 标准UTC时间
        """
        self.logger = logging.getLogger(__name__)
        self.timezone_mode = timezone_mode
        
        # 设置数据目录
        if data_dir is None:
            self.data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'backend', 'data_center', 'kline_data'
            )
        else:
            self.data_dir = data_dir
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 时间框架配置
        self.timeframe_configs = TimeFrameConfig.get_all_configs()
        
        # 指标计算器
        self.indicator_calculator = IndicatorCalculator()
        
        # 数据缓存
        self._data_cache: Dict[str, pd.DataFrame] = {}
        self._indicator_cache: Dict[str, pd.Series] = {}
        
        # 缓存大小限制
        self.max_cache_size = 50
        
        self.logger.info(f"EnhancedKlineManager initialized with data_dir: {self.data_dir}, timezone: {timezone_mode}")
    
    def normalize_timeframe(self, timeframe: str) -> Optional[TimeFrameConfig]:
        """标准化时间框架格式"""
        # 直接匹配
        if timeframe in self.timeframe_configs:
            return self.timeframe_configs[timeframe]
        
        # 尝试匹配文件后缀格式
        for config in self.timeframe_configs.values():
            if config.file_suffix.lower() == timeframe.upper():
                return config
        
        # 尝试匹配TradingView格式
        for config in self.timeframe_configs.values():
            if config.tv_interval.lower() == timeframe.lower():
                return config
        
        self.logger.warning(f"Unknown timeframe format: {timeframe}")
        return None
    
    def get_data_file_path(self, symbol: str, timeframe: str) -> Optional[str]:
        """获取数据文件路径"""
        tf_config = self.normalize_timeframe(timeframe)
        if tf_config is None:
            return None
        
        # 尝试不同的文件名格式
        possible_filenames = [
            f"{symbol}-{tf_config.file_suffix}.csv",
            f"{symbol}-{tf_config.standard_name}.csv",
            f"{symbol}_{tf_config.file_suffix}.csv",
            f"{symbol}_{tf_config.standard_name}.csv",
        ]
        
        for filename in possible_filenames:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                return filepath
        
        self.logger.warning(f"Data file not found for {symbol} {timeframe}")
        return None
    
    def load_raw_data(self, symbol: str, timeframe: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """加载原始K线数据"""
        # 生成缓存键
        cache_key = f"{symbol}_{timeframe}_{start_date}_{end_date}_{self.timezone_mode}"
        
        # 检查缓存
        if cache_key in self._data_cache:
            self.logger.debug(f"Loading data from cache: {cache_key}")
            return self._data_cache[cache_key].copy()
        
        df = None
        
        # 如果指定了时间范围，优先使用OKX API获取实时数据
        if start_date and end_date:
            try:
                from backend.data_center.kline_data.okx_kline_fetcher import OkxKlineFetcher
                okx_fetcher = OkxKlineFetcher(self.data_dir, timezone_mode=self.timezone_mode)
                df = okx_fetcher.get_historical_data(symbol, timeframe, start_date, end_date)
                
                if df is not None and len(df) > 0:
                    self.logger.info(f"从OKX获取到{len(df)}条数据: {symbol} {timeframe} (时区: {self.timezone_mode})")
                    self.logger.info(f"时间范围: {df.index.min()} 到 {df.index.max()}")
                    
                    # 标准化列名
                    df = self._standardize_columns(df)
                    
                    # 缓存数据
                    self._cache_data(cache_key, df)
                    
                    return df.copy()
                else:
                    self.logger.warning(f"OKX返回空数据: {symbol} {timeframe}")
            except Exception as e:
                self.logger.error(f"OKX获取数据失败: {e}")
        
        # 尝试从数据库获取
        try:
            from backend.data_object_center.kline_record import KlineRecord, DatabaseUtils
            session = DatabaseUtils.get_db_session()
            query = session.query(KlineRecord).filter(
                KlineRecord.symbol == symbol.upper(),
                KlineRecord.timeframe == timeframe
            )
            if start_date:
                query = query.filter(KlineRecord.datetime >= start_date)
            if end_date:
                query = query.filter(KlineRecord.datetime <= end_date)
            records = query.order_by(KlineRecord.datetime).all()
            
            if records and len(records) >= 50:
                df = pd.DataFrame([r.to_dict() for r in records])
                df.set_index('datetime', inplace=True)
                self.logger.info(f"从数据库加载{len(df)}条记录: {symbol} {timeframe}")
                
                # 标准化列名
                df = self._standardize_columns(df)
                
                # 缓存数据
                self._cache_data(cache_key, df)
                
                return df.copy()
            else:
                self.logger.info(f"数据库中数据不足: {symbol} {timeframe}")
                
        except Exception as e:
            self.logger.error(f"数据库查询失败: {e}")
        
        # 最后尝试从文件加载（仅作为备用）
        filepath = self.get_data_file_path(symbol, timeframe)
        if filepath and os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                
                # 标准化列名
                df = self._standardize_columns(df)
                
                # 处理时间列
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df = df.set_index('datetime')
                elif df.index.name == 'datetime':
                    df.index = pd.to_datetime(df.index)
                
                # 应用时间过滤
                if start_date:
                    df = df[df.index >= start_date]
                if end_date:
                    df = df[df.index <= end_date]
                
                if len(df) >= 50:
                    # 确保数据按时间排序
                    df = df.sort_index()
                    
                    # 缓存数据
                    self._cache_data(cache_key, df)
                    
                    self.logger.info(f"从文件加载{len(df)}条记录: {symbol} {timeframe}")
                    return df.copy()
                else:
                    self.logger.warning(f"文件数据经过时间过滤后不足: {len(df)} < 50")
                    
            except Exception as e:
                self.logger.error(f"文件加载失败 {filepath}: {e}")
        
        # 如果所有方法都失败，再次尝试用OKX获取更多历史数据
        if df is None or len(df) < 50:
            try:
                from backend.data_center.kline_data.okx_kline_fetcher import OkxKlineFetcher
                okx_fetcher = OkxKlineFetcher(self.data_dir)
                
                # 如果没有指定时间范围，获取最近的数据
                if not start_date and not end_date:
                    df = okx_fetcher.get_recent_data(symbol, timeframe, periods=300)
                else:
                    df = okx_fetcher.get_historical_data(symbol, timeframe, start_date, end_date)
                
                if df is not None and len(df) > 0:
                    self.logger.info(f"OKX备用获取成功: {symbol} {timeframe}, {len(df)}条")
                    
                    # 标准化列名
                    df = self._standardize_columns(df)
                    
                    # 缓存数据
                    self._cache_data(cache_key, df)
                    
                    return df.copy()
                    
            except Exception as e:
                self.logger.error(f"OKX备用获取失败: {e}")
        
        self.logger.error(f"无法获取数据: {symbol} {timeframe}")
        return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        # 标准列名映射
        column_mapping = {
            'Open': 'open', 'OPEN': 'open',
            'High': 'high', 'HIGH': 'high',
            'Low': 'low', 'LOW': 'low',
            'Close': 'close', 'CLOSE': 'close',
            'Volume': 'volume', 'VOLUME': 'volume',
            'Datetime': 'datetime', 'DATETIME': 'datetime',
            'Date': 'datetime', 'DATE': 'datetime',
            'Time': 'datetime', 'TIME': 'datetime',
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df.columns:
                self.logger.warning(f"Missing required column: {col}")
        
        return df
    
    def calculate_indicator(self, df: pd.DataFrame, indicator_request: IndicatorRequest) -> Optional[pd.Series]:
        """计算单个指标"""
        # 检查缓存
        data_hash = hashlib.md5(str(df.index).encode()).hexdigest()[:8]
        cache_key = f"{data_hash}_{indicator_request.cache_key}"
        
        if cache_key in self._indicator_cache:
            self.logger.debug(f"Loading indicator from cache: {indicator_request.name}")
            return self._indicator_cache[cache_key].copy()
        
        try:
            # 获取计算函数
            available_indicators = self.indicator_calculator.get_available_indicators()
            if indicator_request.name not in available_indicators:
                self.logger.error(f"Unknown indicator: {indicator_request.name}")
                return None
            
            calc_func = available_indicators[indicator_request.name]
            
            # 计算指标
            # 过滤掉不属于计算函数的参数
            calc_params = {k: v for k, v in indicator_request.params.items() if k != 'return_index'}
            result = calc_func(df, **calc_params)
            
            # 处理多返回值的情况（如布林带、MACD）
            if isinstance(result, tuple):
                # 对于多返回值，返回第一个值，或者根据参数指定
                if 'return_index' in indicator_request.params:
                    result = result[indicator_request.params['return_index']]
                else:
                    result = result[0]
            
            # 转换为Series
            if not isinstance(result, pd.Series):
                result = pd.Series(result, index=df.index)
            
            # 缓存结果
            self._cache_indicator(cache_key, result)
            
            self.logger.debug(f"Calculated indicator: {indicator_request.name}")
            return result.copy()
            
        except Exception as e:
            self.logger.error(f"Error calculating indicator {indicator_request.name}: {e}")
            return None
    
    def get_data_with_indicators(self, symbol: str, timeframe: str, indicators: List[IndicatorRequest], 
                               start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """获取带指标的数据"""
        # 加载原始数据
        df = self.load_raw_data(symbol, timeframe, start_date, end_date)
        if df is None:
            return None
        
        # 计算指标
        for indicator_req in indicators:
            indicator_data = self.calculate_indicator(df, indicator_req)
            if indicator_data is not None:
                # 生成列名
                if indicator_req.params:
                    params_str = "_".join([f"{k}{v}" for k, v in indicator_req.params.items() if k != 'return_index'])
                    col_name = f"{indicator_req.name}_{params_str}" if params_str else indicator_req.name
                else:
                    col_name = indicator_req.name
                
                df[col_name] = indicator_data
        
        return df
    
    def _cache_data(self, key: str, data: pd.DataFrame):
        """缓存数据"""
        if len(self._data_cache) >= self.max_cache_size:
            # 移除最旧的缓存
            oldest_key = next(iter(self._data_cache))
            del self._data_cache[oldest_key]
        
        self._data_cache[key] = data.copy()
    
    def _cache_indicator(self, key: str, data: pd.Series):
        """缓存指标"""
        if len(self._indicator_cache) >= self.max_cache_size * 2:  # 指标缓存可以更多
            # 移除最旧的缓存
            oldest_key = next(iter(self._indicator_cache))
            del self._indicator_cache[oldest_key]
        
        self._indicator_cache[key] = data.copy()
    
    def clear_cache(self):
        """清空缓存"""
        self._data_cache.clear()
        self._indicator_cache.clear()
        self.logger.info("Cache cleared")
    
    def get_available_symbols(self) -> List[str]:
        """获取可用的交易对"""
        symbols = set()
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                # 提取交易对名称
                symbol_part = filename.replace('.csv', '')
                
                # 移除时间框架后缀
                for tf_config in self.timeframe_configs.values():
                    if symbol_part.endswith(f"-{tf_config.file_suffix}"):
                        symbol = symbol_part[:-len(f"-{tf_config.file_suffix}")]
                        symbols.add(symbol)
                        break
                    elif symbol_part.endswith(f"_{tf_config.file_suffix}"):
                        symbol = symbol_part[:-len(f"_{tf_config.file_suffix}")]
                        symbols.add(symbol)
                        break
        
        return sorted(list(symbols))
    
    def get_available_timeframes(self, symbol: str) -> List[str]:
        """获取指定交易对的可用时间框架"""
        timeframes = []
        
        for tf_config in self.timeframe_configs.values():
            filepath = self.get_data_file_path(symbol, tf_config.standard_name)
            if filepath is not None:
                timeframes.append(tf_config.standard_name)
        
        return timeframes
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换数据类型"""
        if df is None or df.empty:
            return df
        
        try:
            # 确保数值列为float64类型
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
            
            # 确保datetime列为datetime类型
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            elif not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            # 删除任何包含NaN的行
            df = df.dropna(subset=numeric_columns)
            
            # 确保数据按时间排序
            df = df.sort_index()
            
            return df
        except Exception as e:
            self.logger.error(f"数据类型转换失败: {str(e)}")
            return df

    def get_kline_data(self, symbol: str, timeframe: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """获取K线数据"""
        try:
            # 从数据库加载数据
            df = self.load_raw_data(symbol, timeframe, start_date, end_date)
            
            # 如果数据库没有数据，尝试从yfinance下载
            if df is None or len(df) < 50:
                df = self.load_raw_data(symbol, timeframe, start_date, end_date)
            
            if df is not None:
                df = self._convert_data_types(df)
            
            if df is not None:
                self.logger.info(f"{symbol} {timeframe} final rows: {len(df)}, range: {df.index.min()} - {df.index.max()}")
            
            return df
        except Exception as e:
            self.logger.error(f"获取 {symbol} {timeframe} 数据失败: {str(e)}")
            return None
    
    def get_data_info(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """获取数据信息"""
        filepath = self.get_data_file_path(symbol, timeframe)
        if filepath is None:
            return None
        
        try:
            # 读取少量数据获取信息
            df = pd.read_csv(filepath, nrows=5)
            df_full = pd.read_csv(filepath)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'filepath': filepath,
                'total_records': len(df_full),
                'columns': list(df.columns),
                'file_size_mb': round(os.path.getsize(filepath) / 1024 / 1024, 2),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting data info for {symbol} {timeframe}: {e}")
            return None


# 便捷函数
def create_indicator_request(name: str, **params) -> IndicatorRequest:
    """创建指标请求的便捷函数"""
    return IndicatorRequest(name=name, params=params)


# 预定义的常用指标请求
class CommonIndicators:
    """常用指标请求"""
    
    @staticmethod
    def sma(period: int = 20, source: str = 'close') -> IndicatorRequest:
        return create_indicator_request('sma', period=period, source=source)
    
    @staticmethod
    def ema(period: int = 20, source: str = 'close') -> IndicatorRequest:
        return create_indicator_request('ema', period=period, source=source)
    
    @staticmethod
    def rsi(period: int = 14, source: str = 'close') -> IndicatorRequest:
        return create_indicator_request('rsi', period=period, source=source)
    
    @staticmethod
    def bollinger_upper(period: int = 20, std_dev: float = 2.0, source: str = 'close') -> IndicatorRequest:
        return create_indicator_request('bollinger_bands', period=period, std_dev=std_dev, source=source, return_index=0)
    
    @staticmethod
    def bollinger_middle(period: int = 20, std_dev: float = 2.0, source: str = 'close') -> IndicatorRequest:
        return create_indicator_request('bollinger_bands', period=period, std_dev=std_dev, source=source, return_index=1)
    
    @staticmethod
    def bollinger_lower(period: int = 20, std_dev: float = 2.0, source: str = 'close') -> IndicatorRequest:
        return create_indicator_request('bollinger_bands', period=period, std_dev=std_dev, source=source, return_index=2)
    
    @staticmethod
    def adx(period: int = 14) -> IndicatorRequest:
        return create_indicator_request('adx', period=period)


if __name__ == "__main__":
    # 示例用法
    manager = EnhancedKlineManager()
    
    # 获取可用交易对
    symbols = manager.get_available_symbols()
    print(f"Available symbols: {symbols}")
    
    if symbols:
        symbol = symbols[0]
        timeframes = manager.get_available_timeframes(symbol)
        print(f"Available timeframes for {symbol}: {timeframes}")
        
        if timeframes:
            # 获取数据信息
            info = manager.get_data_info(symbol, timeframes[0])
            print(f"Data info: {info}")
            
            # 加载原始数据
            df = manager.load_raw_data(symbol, timeframes[0])
            if df is not None:
                print(f"Loaded data shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                
                # 计算指标
                indicators = [
                    CommonIndicators.sma(20),
                    CommonIndicators.ema(20),
                    CommonIndicators.rsi(14),
                    CommonIndicators.bollinger_upper(20, 2.0),
                    CommonIndicators.bollinger_lower(20, 2.0),
                ]
                
                df_with_indicators = manager.get_data_with_indicators(symbol, timeframes[0], indicators)
                if df_with_indicators is not None:
                    print(f"Data with indicators shape: {df_with_indicators.shape}")
                    print(f"New columns: {list(df_with_indicators.columns)}") 