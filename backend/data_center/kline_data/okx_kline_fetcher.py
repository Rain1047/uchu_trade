#!/usr/bin/env python3
"""
OKX 行情数据拉取器
利用项目现有的 `MarketAPIWrapper` 获取 K 线数据。
目前 `MarketAPIWrapper.get_candlesticks_df` 默认返回最近 `limit` 条数据（OKX 上限 1000）。
本工具：
1. 支持 15m / 1h / 4h / 1d 映射
2. 取回的数据写入 CSV 与 SQLite(kline_record)

依赖: okx-sdk-python / pandas
"""
import os
import logging
from typing import Optional

import pandas as pd
from datetime import datetime

from backend._utils import ConfigUtils
from backend.api_center.okx_api.market_api import MarketAPIWrapper

logger = logging.getLogger(__name__)

_BAR_MAPPING = {
    '15m': '15m',
    '30m': '30m',
    '1h': '1H',
    '4h': '4H',
    '1d': '1D',
}


class OkxKlineFetcher:
    def __init__(self, data_dir: str):
        cfg = ConfigUtils.get_config()
        self.data_dir = data_dir
        self.market = MarketAPIWrapper(
            cfg['okx_api_key_demo'],  # 使用 demo key
            cfg['okx_secret_key_demo'],
            cfg['passphrase'],
            flag='1'  # demo 环境
        )

    def _get_filepath(self, symbol: str, timeframe: str):
        return os.path.join(self.data_dir, f"{symbol}-{timeframe.upper()}.csv")

    def download_historical(self, symbol: str, timeframe: str, limit: str = '1000'):
        if timeframe not in _BAR_MAPPING:
            logger.warning(f"[OKX] 不支持的时间框架: {timeframe}")
            return
        bar = _BAR_MAPPING[timeframe]
        instId = symbol.upper() + "-USDT"
        logger.info(f"[OKX] 拉取 {instId} {bar} k线, limit={limit}")
        try:
            data_df = self.market.get_candlesticks_df(instId=instId, bar=bar)
        except Exception as e:
            logger.error(f"[OKX] 获取失败: {e}")
            return
        if data_df is None or data_df.empty:
            logger.warning("[OKX] 返回数据为空")
            return

        data_df.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'volume'}, inplace=True)
        data_df.reset_index(inplace=True)
        data_df.rename(columns={'timestamp': 'datetime'}, inplace=True)

        # OKX 返回的 timestamp 为毫秒字符串 → 转 datetime
        try:
            data_df['datetime'] = pd.to_datetime(data_df['datetime'].astype(int), unit='ms')
        except Exception:
            data_df['datetime'] = pd.to_datetime(data_df['datetime'])

        filepath = self._get_filepath(symbol, timeframe)
        data_df.to_csv(filepath, index=False)
        logger.info(f"[OKX] 保存 CSV {filepath}, 行数 {len(data_df)}")

        # 写入数据库
        try:
            from backend.data_object_center.kline_record import KlineRecord, DatabaseUtils
            session = DatabaseUtils.get_db_session()
            records = []
            for _, row in data_df.iterrows():
                records.append(
                    KlineRecord(
                        symbol=symbol.upper(),
                        timeframe=timeframe,
                        datetime=row['datetime'].to_pydatetime() if hasattr(row['datetime'], 'to_pydatetime') else row['datetime'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row.get('volume', 0))
                    )
                )
            KlineRecord.bulk_upsert(session, records)
            logger.info(f"[OKX] 已同步 {symbol} {timeframe} 数据到数据库")
        except Exception as e:
            logger.error(f"[OKX] 写入数据库失败: {e}") 