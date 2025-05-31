#!/usr/bin/env python3
"""
使用 yfinance 下载加密货币 K 线并写入 CSV + SQLite
- yfinance 间隔支持到 1h；如需 4h 则对 1h 数据重采样
- 网络要求较宽松，无需访问交易所 REST

依赖: pip install yfinance pandas
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

_YF_INTERVALS = {
    '15m': '15m',
    '30m': '30m',
    '1h': '60m',
    '4h': '60m',  # 先拉 1h 再重采样
    '1d': '1d',
}


class YFinanceKlineFetcher:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def _get_filepath(self, symbol: str, timeframe: str) -> str:
        return os.path.join(self.data_dir, f"{symbol}-{timeframe.upper()}.csv")

    def _download_yf(self, ticker: str, interval: str, start: Optional[str] = None, end: Optional[str] = None):
        return yf.download(tickers=ticker, interval=interval, start=start, end=end, progress=False, threads=True)

    def download_historical(self, symbol: str, timeframe: str,
                            start: Optional[str] = None, end: Optional[str] = None):
        if timeframe not in _YF_INTERVALS:
            logger.warning(f"[YF] 不支持的时间框架: {timeframe}")
            return
        interval = _YF_INTERVALS[timeframe]
        ticker = symbol.upper() + "-USD"
        filepath = self._get_filepath(symbol, timeframe)

        logger.info(f"[YF] 开始下载 {symbol} {timeframe} 数据 via yfinance, interval={interval}")

        try:
            df = self._download_yf(ticker, interval, start, end)
        except Exception as e:
            logger.error(f"[YF] 下载失败: {e}")
            return

        if df.empty:
            logger.warning("[YF] 未获取到任何数据")
            return

        # 处理重采样 (4h)
        if timeframe == '4h':
            df = df.resample('4H').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()

        # 标准化列并重命名匹配系统
        df.reset_index(inplace=True)
        df.rename(columns={
            'Datetime': 'datetime',
            'Date': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)

        # 写入 CSV
        df.to_csv(filepath, index=False)
        logger.info(f"[YF] 已保存 CSV {filepath}, 行数 {len(df)}")

        # 写入数据库
        try:
            from backend.data_object_center.kline_record import KlineRecord, DatabaseUtils
            session = DatabaseUtils.get_db_session()
            records = [
                KlineRecord(symbol=symbol.upper(), timeframe=timeframe, datetime=row['datetime'],
                             open=row['open'], high=row['high'], low=row['low'], close=row['close'],
                             volume=row.get('volume', 0))
                for _, row in df.iterrows()
            ]
            KlineRecord.bulk_upsert(session, records)
            logger.info(f"[YF] 已同步 {symbol} {timeframe} 数据到数据库")
        except Exception as e:
            logger.error(f"[YF] 写入数据库失败: {e}") 