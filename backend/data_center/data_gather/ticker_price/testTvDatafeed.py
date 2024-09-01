import os

import pandas as pd
from tvDatafeed import TvDatafeed, Interval

username = '3487851868@qq.com'
password = 'Xiaoyu19971104!'


import yfinance as yf


if __name__ == '__main__':
    tv = TvDatafeed(username, password)
    symbol = 'BTCUSDT'
    interval = Interval.in_4_hour
    nifty_index_data = tv.get_hist(symbol=symbol,
                                   exchange='Binance',
                                   interval=interval,
                                   n_bars=50)
    # nifty_index_data.to_csv(f'{symbol}-{interval.value}.csv')
    # 检查文件是否存在

    # 定义CSV文件名
    filename = f'{symbol}-{interval.value}.csv'

    # 检查文件是否存在
    if not os.path.exists(filename):
        # 如果文件不存在，创建新文件并保存数据（包括表头）
        nifty_index_data.to_csv(filename, index=True)
    else:
        # 如果文件存在，追加数据（不包括表头）
        nifty_index_data.to_csv(filename, mode='a', header=False, index=True)

    print(nifty_index_data.head())

    # # 下载 VIX 指数数据
    # vix = yf.download('^VIX', start='2020-01-01', end='2023-12-31')
    #
    # # 显示数据
    # print(vix.head())



