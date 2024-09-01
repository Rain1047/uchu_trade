import os

import pandas as pd
from tvDatafeed import TvDatafeed, Interval

username = '3487851868@qq.com'
password = 'Xiaoyu19971104!'

import yfinance as yf
if __name__ == '__main__':
    tv = TvDatafeed(username, password)
    suffix = "USDT"
    symbol = 'SOL' + suffix
    interval = Interval.in_daily
    df = tv.get_hist(symbol=symbol,
                     exchange='Binance',
                     interval=interval,
                     n_bars=5000)
    # nifty_index_data.to_csv(f'{symbol}-{interval.value}.csv')
    # 检查文件是否存在

    # 定义CSV文件名
    filename = f'{symbol}-{interval.value}.csv'

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

    print(df.head())
    print(df.dtypes)
    print(df.index)

    # # 下载 VIX 指数数据
    # vix = yf.download('^VIX', start='2020-01-01', end='2023-12-31')
    #
    # # 显示数据
    # print(vix.head())
