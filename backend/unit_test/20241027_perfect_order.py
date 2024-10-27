import numpy as np
from backend.data_center.kline_data.kline_data_collector import *


def perfect_order_strategy(df: DataFrame) -> DataFrame:
    if 'high' not in df.columns or 'low' not in df.columns or 'close' not in df.columns:
        raise ValueError("DataFrame must contain 'high', 'low', and 'close' columns.")
    df['is_perfect_order'] = (df['sma10'] > df['sma20']) & (df['sma20'] > df['sma50']) & (
                df['sma50'] > df['sma100']) & (df['sma100'] > df['sma200'])
    df['is_prev_perfect_order'] = df['is_perfect_order'].shift(1)
    # 当前一个不是完美订单，而今天是完美订单，则买入
    df['buy_sig'] = np.where((df['is_perfect_order'] == True) & (df['is_prev_perfect_order'] == False), 0, 1)
    df['sell_sig'] = np.where((df['is_perfect_order'] == False) & (df['is_prev_perfect_order'] == True), 0, 1)

    return KlineDataProcessor.format_result(df)


if __name__ == '__main__':
    tv = KlineDataCollector()
    file_abspath = tv.get_abspath(symbol='BTC', interval=Interval.in_daily)
    df = pd.read_csv(f"{file_abspath}")
    result = perfect_order_strategy(df)
    print(result)
