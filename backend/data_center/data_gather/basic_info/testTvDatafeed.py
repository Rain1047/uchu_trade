from tvDatafeed import TvDatafeed, Interval

username = '3487851868@qq.com'
password = 'Xiaoyu19971104!'

if __name__ == '__main__':
    tv = TvDatafeed(username, password)
    nifty_index_data = tv.get_hist(symbol='NIFTY',
                                   exchange='NSE',
                                   interval=Interval.in_1_hour,
                                   n_bars=1000)
    # nifty_index_data.to_csv('nifty_index_data.csv')


