from pandas import DataFrame


def sma_perfect_order_filter_strategy(df: DataFrame) -> DataFrame:
    if not df.empty:
        df['sma10_diff_sma20'] = df['sma10'] - df['sma20']
        df['prev_sma10_diff_sma20_1'] = df['sma10_diff_sma20'].shift(1)
        buy_mask = df['sma10_diff_sma20'] > df['prev_sma10_diff_sma20_1']
        df.loc[~buy_mask, 'entry_sig'] = 0
        df.drop(['sma10_diff_sma20', 'prev_sma10_diff_sma20_1'], axis=1, inplace=True)
    return df
