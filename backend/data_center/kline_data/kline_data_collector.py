import logging
import os
from typing import Optional, Dict, List

import pandas as pd
from pandas import DataFrame
from tvDatafeed import TvDatafeed, Interval

from backend.data_center.data_object.enum_obj import EnumTimeFrame
from backend.data_center.kline_data.kline_data_processor import KlineDataProcessor
from backend.object_center.object_dao.symbol_instance import query_all_symbol_instance, SymbolInstance
from backend.utils.utils import ConfigUtils


class KlineDataCollector:

    def __init__(self):
        self._load_config()
        self.tv = TvDatafeed(self.config['tradingview_account'],
                             self.config['tradingview_password'])
        self.logger = logging.getLogger(__name__)
        # 设置数据保存目录
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'backend',
            'data_center',
            'kline_data'
        )
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_config(self):
        self.config = ConfigUtils.get_config()

    def collect_data(self, ticker: str, interval: Interval):
        df = self.tv.get_hist(symbol=ticker + "USDT",
                              exchange='Binance',
                              interval=interval,
                              n_bars=5000)
        df = KlineDataProcessor.add_indicator(df)
        # 定义CSV文件名
        filename = f'{ticker}-{interval.value}.csv'

        # 使用正确的文件路径
        filepath = os.path.join(self.data_dir, f'{ticker}-{interval.value}.csv')
        if os.path.exists(filepath):
            # 如果文件存在，读取已有数据
            existing_data = pd.read_csv(filepath, index_col='datetime', parse_dates=True)

            # 合并新数据与已有数据，并去除重复
            combined_data = pd.concat([existing_data, df])
            combined_data = combined_data[~combined_data.index.duplicated(keep='last')]

            # 按时间顺序排序
            combined_data.sort_index(inplace=True)

            # 保存合并后的数据
            combined_data.to_csv(filepath, index=True)
        else:
            # 如果文件不存在，直接保存数据（包括表头）
            df.to_csv(filepath, mode='a', index=True)

    def batch_collect_data(self) -> Dict:
        interval_list = ['1D', '4H']
        try:
            item_list: List[SymbolInstance] = query_all_symbol_instance()
            for item in item_list:
                for interval in interval_list:
                    self.collect_data(item.symbol, Interval(interval))
                    print(f"{item.symbol} Collecting Finished.")
            print("Batch Collecting Finished.")
            return {
                "success": True,
                "date": len(item_list)
            }
        except Exception as e:
            self.logger.error(f"batch collect data error:{e}")
            return {
                "success": False,
                "data": 0
            }

    @staticmethod
    def query_kline_data(symbol: str, interval: Interval) -> DataFrame:
        # 获取正确的文件路径
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'backend',
            'data_center',
            'kline_data'
        )
        filepath = os.path.join(data_dir, f'{symbol}-{interval.value}.csv')
        # 定义CSV文件名
        filename = f'{symbol}-{interval.value}.csv'
        if os.path.exists(filepath):
            return pd.read_csv(filepath, index_col='datetime')
        else:
            # 创建空dataframe
            return pd.DataFrame()

    @staticmethod
    def get_abspath(symbol: Optional[str], interval: Optional[EnumTimeFrame]) -> str:
        # 获取正确的目录路径
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'backend',
            'data_center',
            'kline_data'
        )
        if symbol is None or interval is None:
            return data_dir
        else:
            file_name = f'{symbol}-{interval.value}.csv'
            return os.path.join(data_dir, file_name)
        #
        # # Get the directory of the current script
        # if symbol is None or interval is None:
        #     print(os.path.dirname(os.path.realpath(__file__)))
        #     return os.path.dirname(os.path.realpath(__file__))
        # else:
        #     file_name = f'{symbol}-{interval.value}.csv'
        #     return os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)


def query_kline_data(symbol: str, interval: Interval) -> DataFrame:
    # 定义CSV文件名
    filename = f'{symbol}-{interval.value}.csv'
    if os.path.exists(filename):
        return pd.read_csv(filename, index_col='datetime')
    else:
        # 创建空dataframe
        return pd.DataFrame()


if __name__ == '__main__':
    tv = KlineDataCollector()
    # tv.collect_data('BTC', Interval.in_daily)

    tv.batch_collect_data()

    # tv.get_abspath()
    #
    # collect_list: List[SymbolInstance] = query_all_symbol_instance()
    # for collect in collect_list:
    #     print(collect.symbol, collect.interval)
    #     tv.collect_data(collect.symbol, Interval(collect.interval))
    # tv.batch_collect_data()
    # df = query_kline_data('BTC', Interval.in_daily)
    # print(df.dtypes)
    # print(df.index)
