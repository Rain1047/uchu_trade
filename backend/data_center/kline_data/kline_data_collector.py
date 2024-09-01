import os

import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backend.service.utils import ConfigUtils
from backend.data_center.data_object.dao.symbol_instance import *


class KlineDataCollector:

    def __init__(self):
        self._load_config()
        self.tv = TvDatafeed(self.config['tradingview_account'],
                             self.config['tradingview_password'])

    def _load_config(self):
        self.config = ConfigUtils.get_config()

    def collect_data(self, ticker: str, interval: Interval):
        df = self.tv.get_hist(symbol=ticker + "USDT",
                              exchange='Binance',
                              interval=interval,
                              n_bars=5000)
        # 定义CSV文件名
        filename = f'{ticker}-{interval.value}.csv'
        if os.path.exists(filename):
            # 如果文件存在，读取已有数据
            existing_data = pd.read_csv(filename, index_col='datetime', parse_dates=True)

            # 合并新数据与已有数据，并去除重复
            combined_data = pd.concat([existing_data, df])
            combined_data = combined_data[~combined_data.index.duplicated(keep='last')]

            # 按时间顺序排序
            combined_data.sort_index(inplace=True)

            # 保存合并后的数据
            combined_data.to_csv(filename, index=True)
        else:
            # 如果文件不存在，直接保存数据（包括表头）
            df.to_csv(filename, mode='a', index=True)


if __name__ == '__main__':
    tv = KlineDataCollector()
    tv.collect_data('SOL', Interval.in_daily)

    collect_list: List[SymbolInstance] = query_all_symbol_instance()
    for collect in collect_list:
        print(collect.symbol, collect.interval)
        tv.collect_data(collect.symbol, Interval(collect.interval))
