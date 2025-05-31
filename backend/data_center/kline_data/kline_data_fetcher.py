#!/usr/bin/env python3
"""
Kline 数据自动拉取器
- 基于 ccxt 从 Binance 免费接口获取历史 OHLCV
- 支持 15m / 1h / 4h / 1d 等常用时间框架
- 自动增量更新并写入 CSV，与 EnhancedKlineManager 使用的目录保持一致

依赖: pip install ccxt pandas
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

import ccxt
import pandas as pd

logger = logging.getLogger(__name__)

# Binance 允许一次最多 1000 根 K 线
_MAX_LIMIT = 1000

# ccxt 时间框架映射（ccxt 与 Binance REST 一致）
_CCXT_TIMEFRAMES = {
    '15m': '15m',
    '30m': '30m',
    '1h': '1h',
    '2h': '2h',
    '4h': '4h',
    '6h': '6h',
    '12h': '12h',
    '1d': '1d',
}


def _to_millis(dt: datetime) -> int:
    """datetime 转毫秒"""
    return int(dt.timestamp() * 1000)


def _from_millis(ms: int) -> datetime:
    return datetime.utcfromtimestamp(ms / 1000)


class BinanceKlineFetcher:
    """使用 ccxt 从 Binance 获取历史行情"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.exchange = ccxt.binance()

    def _get_filepath(self, symbol: str, timeframe: str) -> str:
        return os.path.join(self.data_dir, f"{symbol}-{timeframe.upper()}.csv")

    def download_historical(self, symbol: str, timeframe: str,
                            start: Optional[str] = None,
                            end: Optional[str] = None) -> None:
        """下载并保存历史数据，如文件已存在则增量更新"""
        assert timeframe in _CCXT_TIMEFRAMES, f"不支持的时间框架: {timeframe}"
        tf = _CCXT_TIMEFRAMES[timeframe]
        filepath = self._get_filepath(symbol, timeframe)

        # 将 symbol 转换为交易对，例如 BTC -> BTC/USDT
        market_symbol = symbol.upper() + "/USDT"

        # 先读取已有数据，以便增量下载
        if os.path.exists(filepath):
            existing_df = pd.read_csv(filepath)
            if not existing_df.empty:
                last_ts = pd.to_datetime(existing_df["datetime"]).max()
                # Binance 的 OHLCV 返回的是毫秒时间戳
                since_ms = _to_millis(last_ts) + 1
            else:
                since_ms = _to_millis(datetime.utcnow() - timedelta(days=365 * 3))  # 默认拉3年
        else:
            existing_df = pd.DataFrame()
            if start:
                since_ms = _to_millis(pd.to_datetime(start))
            else:
                since_ms = _to_millis(datetime.utcnow() - timedelta(days=365 * 3))

        if end:
            end_ms = _to_millis(pd.to_datetime(end))
        else:
            end_ms = _to_millis(datetime.utcnow())

        all_records = []
        fetch_since = since_ms
        logger.info(f"[Fetcher] 开始下载 {symbol} {timeframe} 数据: {datetime.utcfromtimestamp(fetch_since/1000)} -> {datetime.utcfromtimestamp(end_ms/1000)}")

        while fetch_since < end_ms:
            try:
                ohlcv = self.exchange.fetch_ohlcv(market_symbol, timeframe=tf, since=fetch_since, limit=_MAX_LIMIT)
            except Exception as e:
                logger.error(f"[Fetcher] fetch_ohlcv 出错: {e}")
                time.sleep(1)
                continue
            if not ohlcv:
                break

            # 更新 since
            fetch_since = ohlcv[-1][0] + 1
            all_records.extend(ohlcv)
            # 避免请求过快
            time.sleep(self.exchange.rateLimit / 1000)

        if not all_records:
            logger.warning("[Fetcher] 未获取到任何数据")
            return

        # 转成 DataFrame
        df_new = pd.DataFrame(all_records, columns=["ts", "open", "high", "low", "close", "volume"])
        df_new["datetime"] = pd.to_datetime(df_new["ts"], unit="ms")
        df_new.drop(columns=["ts"], inplace=True)

        # 合并去重
        combined = pd.concat([existing_df, df_new]).drop_duplicates(subset=["datetime"]).sort_values("datetime")

        # 写入 CSV
        combined.to_csv(filepath, index=False)

        # —— 写入数据库 ——
        try:
            from backend.data_object_center.kline_record import KlineRecord, DatabaseUtils
            session = DatabaseUtils.get_db_session()
            records = []
            for _, row in combined.iterrows():
                records.append(
                    KlineRecord(
                        symbol=symbol.upper(),
                        timeframe=timeframe,
                        datetime=row['datetime'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row.get('volume', 0)
                    )
                )
            KlineRecord.bulk_upsert(session, records)
            logger.info(f"[Fetcher] 已同步 {symbol} {timeframe} 数据到数据库, 行数 {len(combined)}")
        except Exception as e:
            logger.error(f"[Fetcher] 写入数据库失败: {e}")

        logger.info(f"[Fetcher] 保存 {symbol}-{timeframe.upper()}.csv & DB, 共 {len(combined)} 行") 