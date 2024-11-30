import os
from typing import Optional

import pandas as pd
from pandas import DataFrame


class KlineDataReader:

    @staticmethod
    def query_kline_data(symbol: str, interval: str) -> DataFrame:
        # 定义CSV文件名
        filename = f'{symbol}-{interval}.csv'
        if os.path.exists(filename):
            return pd.read_csv(filename, index_col='datetime')
        else:
            # 创建空dataframe
            return pd.DataFrame()

    @staticmethod
    def get_abspath(symbol: Optional[str], interval: Optional[str]) -> str:
        # Get the directory of the current script
        if symbol is None or interval is None:
            print(os.path.dirname(os.path.realpath(__file__)))
            return os.path.dirname(os.path.realpath(__file__))
        else:
            file_name = f'{symbol}-{interval}.csv'
            return os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)


if __name__ == '__main__':
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
    pass

if __name__ == '__main__':
    kline_reader = KlineDataReader()
    result = kline_reader.query_kline_data('DOGE', '1D')
    print(result)
