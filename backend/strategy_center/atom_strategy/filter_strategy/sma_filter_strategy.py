from pandas import DataFrame


def sam_filter_strategy_for_backtest(df: DataFrame) -> DataFrame:
    if not df.empty:
        buy_mask = (df['sma10'] > df['sma20']) & (df['sma20'] > df['sma50'])
        df.loc[~buy_mask, 'entry_sig'] = 0
    return df
