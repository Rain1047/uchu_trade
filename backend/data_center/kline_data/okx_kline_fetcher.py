#!/usr/bin/env python3
"""
OKX K线数据获取器
- 使用OKX API获取实时K线数据
- 支持根据回测期间动态获取数据
- 时间范围过滤
- 支持多时区日线边界（中国时间8点 或 美国东部时间0点）
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import pytz

from backend.api_center.okx_api.okx_main import OKXAPIWrapper
from backend._utils import LogConfig

logger = LogConfig.get_logger(__name__)

class OkxKlineFetcher:
    """OKX K线数据获取器"""
    
    def __init__(self, data_dir: str, timezone_mode: str = "UTC-4"):
        """
        初始化OKX K线数据获取器
        
        Args:
            data_dir: 数据目录
            timezone_mode: 时区模式，支持:
                - "UTC+8": 中国时间，日线以8:00为边界
                - "UTC-4": 美国东部时间，日线以0:00为边界
                - "UTC": 标准UTC时间
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 设置时区模式
        self.timezone_mode = timezone_mode
        self._setup_timezone()
        
        # 初始化OKX API
        try:
            self.okx_api = OKXAPIWrapper()
            logger.info("OKX API初始化成功")
        except Exception as e:
            logger.error(f"OKX API初始化失败: {e}")
            self.okx_api = None
    
    def _setup_timezone(self):
        """设置时区配置"""
        self.utc_tz = pytz.UTC
        
        if self.timezone_mode == "UTC+8":
            self.local_tz = pytz.timezone('Asia/Shanghai')
            self.boundary_hour = 8  # 中国时间8点
            self.tz_name = "中国时间"
        elif self.timezone_mode == "UTC-4":
            self.local_tz = pytz.timezone('US/Eastern')  # 美国东部时间
            self.boundary_hour = 0  # 美国东部时间0点（午夜）
            self.tz_name = "美国东部时间"
        else:  # UTC
            self.local_tz = self.utc_tz
            self.boundary_hour = 0
            self.tz_name = "UTC时间"
            
        logger.info(f"时区模式: {self.timezone_mode} ({self.tz_name}), 日线边界: {self.boundary_hour}:00")
    
    def _convert_timeframe(self, timeframe: str) -> str:
        """转换时间框架格式到OKX格式"""
        timeframe_mapping = {
            '1m': '1m',
            '5m': '5m', 
            '15m': '15m',
            '30m': '30m',
            '1h': '1H',
            '2h': '2H',
            '4h': '4H',
            '6h': '6H',
            '12h': '12H',
            '1d': '1D',
            '3d': '3D',
            '1w': '1W',
        }
        return timeframe_mapping.get(timeframe.lower(), '1D')
    
    def _convert_symbol(self, symbol: str) -> str:
        """转换交易对格式到OKX格式"""
        if 'USDT' in symbol.upper():
            return symbol.upper()
        elif '-' in symbol:
            return symbol.upper()
        else:
            return f"{symbol.upper()}-USDT"
    
    def _get_filepath(self, symbol: str, timeframe: str) -> str:
        """获取数据文件路径"""
        clean_symbol = symbol.replace('-', '').replace('USDT', '')
        return os.path.join(self.data_dir, f"{clean_symbol}-{timeframe.upper()}.csv")
    
    def _adjust_time_for_timezone(self, start_date: str, end_date: str, timeframe: str) -> tuple:
        """根据设定时区调整时间范围"""
        if timeframe != '1d' or self.timezone_mode == "UTC":
            # 非日线数据或UTC模式不需要特殊处理
            return start_date, end_date
        
        try:
            # 解析输入的日期
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # 为日期添加指定时区的边界时间
            start_local = self.local_tz.localize(start_dt.replace(
                hour=self.boundary_hour, minute=0, second=0, microsecond=0
            ))
            end_local = self.local_tz.localize(end_dt.replace(
                hour=self.boundary_hour, minute=0, second=0, microsecond=0
            ))
            
            # 转换为UTC时间（OKX API使用UTC）
            start_utc = start_local.astimezone(self.utc_tz)
            end_utc = end_local.astimezone(self.utc_tz)
            
            logger.info(f"时间范围调整({self.timezone_mode}):")
            logger.info(f"  输入: {start_date} ~ {end_date}")
            logger.info(f"  {self.tz_name}: {start_local} ~ {end_local}")
            logger.info(f"  UTC时间: {start_utc} ~ {end_utc}")
            
            return start_utc.strftime('%Y-%m-%d %H:%M:%S'), end_utc.strftime('%Y-%m-%d %H:%M:%S')
            
        except Exception as e:
            logger.error(f"时间转换失败: {e}")
            return start_date, end_date
    
    def _convert_utc_to_local_display(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """将UTC时间转换为本地时间显示"""
        if timeframe != '1d' or self.timezone_mode == "UTC":
            return df
        
        try:
            # 转换索引时间为本地时间显示
            local_times = []
            for utc_time in df.index:
                if utc_time.tzinfo is None:
                    utc_time = self.utc_tz.localize(utc_time)
                local_time = utc_time.astimezone(self.local_tz)
                
                # 对于日线数据，显示边界时间
                local_date = local_time.date()
                if self.timezone_mode == "UTC-4":
                    # 美国东部时间显示午夜0:00
                    boundary_time = self.local_tz.localize(datetime.combine(
                        local_date, datetime.min.time().replace(hour=0)
                    ))
                else:
                    # 中国时间显示8:00
                    boundary_time = self.local_tz.localize(datetime.combine(
                        local_date, datetime.min.time().replace(hour=self.boundary_hour)
                    ))
                local_times.append(boundary_time)
            
            # 创建新的DataFrame，使用本地时间索引
            df_local = df.copy()
            df_local.index = local_times
            
            logger.info(f"时间显示转换完成({self.tz_name})，时间范围: {df_local.index.min()} ~ {df_local.index.max()}")
            return df_local
            
        except Exception as e:
            logger.error(f"时间显示转换失败: {e}")
            return df
    
    def get_historical_data(self, symbol: str, timeframe: str, 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None,
                           limit: int = 300) -> Optional[pd.DataFrame]:
        """获取历史K线数据"""
        if self.okx_api is None:
            logger.error("OKX API未初始化")
            return None
        
        try:
            # 转换格式
            okx_symbol = self._convert_symbol(symbol)
            okx_timeframe = self._convert_timeframe(timeframe)
            
            logger.info(f"从OKX获取数据: {okx_symbol} {okx_timeframe} (时区: {self.timezone_mode})")
            
            # 根据设定时区调整时间范围
            if start_date and end_date:
                adjusted_start, adjusted_end = self._adjust_time_for_timezone(start_date, end_date, timeframe)
                start_dt = pd.to_datetime(adjusted_start)
                end_dt = pd.to_datetime(adjusted_end)
                
                # 根据时间框架计算需要的K线数量
                if timeframe == '1d':
                    required_bars = (end_dt - start_dt).days + 1
                elif timeframe == '4h':
                    required_bars = (end_dt - start_dt).days * 6 + 1
                elif timeframe == '1h':
                    required_bars = (end_dt - start_dt).days * 24 + 1
                else:
                    required_bars = limit
                
                # OKX最多返回300根K线，如果需要更多则分批获取
                limit = min(required_bars, 300)
            
            # 调用OKX API获取数据
            response = self.okx_api.market_api.get_candlesticks(
                instId=okx_symbol,
                bar=okx_timeframe,
                limit=str(limit)
            )
            
            if not response or 'data' not in response:
                logger.error(f"OKX API返回数据为空: {response}")
                return None
            
            data = response['data']
            if not data:
                logger.warning(f"OKX返回的数据列表为空")
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(data, columns=[
                'datetime', 'open', 'high', 'low', 'close', 'volume',
                'volCcy', 'volCcyQuote', 'confirm'
            ])
            
            # 数据类型转换
            df['datetime'] = pd.to_datetime(df['datetime'].astype(int), unit='ms', utc=True)
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # 设置索引
            df = df.set_index('datetime')
            
            # 只保留需要的列
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            # 添加symbol列
            df['symbol'] = f"Binance:{okx_symbol.replace('-', '')}"
            
            # 时间范围过滤（基于UTC时间）
            if start_date and end_date:
                adjusted_start, adjusted_end = self._adjust_time_for_timezone(start_date, end_date, timeframe)
                start_utc = pd.to_datetime(adjusted_start, utc=True)
                end_utc = pd.to_datetime(adjusted_end, utc=True)
                
                df = df[df.index >= start_utc]
                df = df[df.index <= end_utc]
            
            # 按时间排序
            df = df.sort_index()
            
            # 转换为本地时间显示（仅对日线数据）
            if timeframe == '1d':
                df = self._convert_utc_to_local_display(df, timeframe)
            
            logger.info(f"成功获取{len(df)}条数据，时间范围: {df.index.min()} 到 {df.index.max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"获取OKX数据失败: {e}")
            return None
    
    def download_historical(self, symbol: str, timeframe: str,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> bool:
        """下载并保存历史数据"""
        try:
            df = self.get_historical_data(symbol, timeframe, start_date, end_date)
            
            if df is None or df.empty:
                logger.error("未能获取有效数据")
                return False
            
            # 保存到文件
            filepath = self._get_filepath(symbol, timeframe)
            
            # 如果文件已存在，合并数据
            if os.path.exists(filepath):
                try:
                    existing_df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
                    # 合并新旧数据，去重
                    combined_df = pd.concat([existing_df, df]).drop_duplicates().sort_index()
                    df = combined_df
                except Exception as e:
                    logger.warning(f"合并已有数据失败，将覆盖: {e}")
            
            # 重置索引以保存datetime列
            df_to_save = df.reset_index()
            df_to_save.to_csv(filepath, index=False)
            
            logger.info(f"数据已保存到: {filepath}")
            logger.info(f"保存了{len(df)}条数据")
            
            return True
            
        except Exception as e:
            logger.error(f"下载数据失败: {e}")
            return False
    
    def get_recent_data(self, symbol: str, timeframe: str, periods: int = 100) -> Optional[pd.DataFrame]:
        """获取最近的K线数据"""
        return self.get_historical_data(symbol, timeframe, limit=periods)


if __name__ == "__main__":
    # 测试代码 - 比较不同时区的效果
    
    # 测试UTC-4（美国东部时间）
    print("=== 测试美国东部时间UTC-4边界处理 ===")
    fetcher_us = OkxKlineFetcher("/tmp/test_data", timezone_mode="UTC-4")
    df_us = fetcher_us.get_historical_data("BTC", "1d", 
                                          start_date="2025-05-29", 
                                          end_date="2025-05-31")
    
    if df_us is not None:
        print(f"获取到{len(df_us)}条数据（美国东部时间）")
        print("\n每日数据详情（美国东部时间）:")
        for idx, row in df_us.iterrows():
            date_str = idx.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"  {date_str}: 开盘={row['open']:.1f}, 收盘={row['close']:.1f}")
        
        print(f"\n时间范围: {df_us.index.min()} 到 {df_us.index.max()}")
        print("\n说明（美国东部时间）：")
        print("- 每个日期显示的是美国东部时间0:00（午夜）")
        print("- 5月31日的数据实际代表5月30日0:00到5月31日0:00的交易数据")
        print("- 5月30日的数据实际代表5月29日0:00到5月30日0:00的交易数据")
    else:
        print("未能获取美国东部时间数据")
    
    print("\n" + "="*60)
    
    # 测试UTC+8（中国时间）进行对比
    print("=== 测试中国时间UTC+8边界处理（对比） ===")
    fetcher_cn = OkxKlineFetcher("/tmp/test_data", timezone_mode="UTC+8")
    df_cn = fetcher_cn.get_historical_data("BTC", "1d", 
                                          start_date="2025-05-29", 
                                          end_date="2025-05-31")
    
    if df_cn is not None:
        print(f"获取到{len(df_cn)}条数据（中国时间）")
        print("\n每日数据详情（中国时间）:")
        for idx, row in df_cn.iterrows():
            date_str = idx.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"  {date_str}: 开盘={row['open']:.1f}, 收盘={row['close']:.1f}")
        
        print(f"\n时间范围: {df_cn.index.min()} 到 {df_cn.index.max()}")
        print("\n说明（中国时间）：")
        print("- 每个日期显示的是中国时间8:00")
        print("- 5月31日的数据实际代表5月30日8:00到5月31日8:00的交易数据")
    else:
        print("未能获取中国时间数据")
    
    print("\n" + "="*60)
    print("=== 时区对比总结 ===")
    if df_us is not None and df_cn is not None:
        print("UTC-4 vs UTC+8 时差: 12小时")
        print("这意味着美国东部时间的日线边界比中国时间早12小时")
        print("例如：美国5月31日0:00 = 中国5月31日12:00")
        
        # 比较相同日期的数据差异
        if len(df_us) > 0 and len(df_cn) > 0:
            us_last = df_us.iloc[-1]
            cn_last = df_cn.iloc[-1]
            print(f"\n数据对比（最新一天）：")
            print(f"美国时间收盘价: {us_last['close']:.1f}")
            print(f"中国时间收盘价: {cn_last['close']:.1f}")
            print(f"价格差异: {abs(us_last['close'] - cn_last['close']):.1f}") 