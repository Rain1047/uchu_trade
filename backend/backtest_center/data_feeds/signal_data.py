from typing import Optional
import backtrader as bt
import pandas as pd


class SignalData(bt.feeds.PandasData):
    """
    自定义数据源类，扩展了标准K线数据，添加了信号相关的数据列

    Additional Lines:
        entry_sig: 入场信号
        entry_price: 入场价格
        sell_sig: 卖出信号
        sell_price: 卖出价格
    """
    lines = ('entry_sig', 'entry_price', 'sell_sig', 'sell_price',)
    params = (
        ('datetime', 'datetime'),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('entry_sig', 'entry_sig'),
        ('entry_price', 'entry_price'),
        ('sell_sig', 'sell_sig'),
        ('sell_price', 'sell_price'),
    )

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, datetime_col: str = 'datetime') -> 'SignalData':
        """
        从DataFrame创建数据源

        Args:
            df: 包含所需数据的DataFrame
            datetime_col: 日期时间列的名称

        Returns:
            SignalData: 数据源实例
        """
        # 确保datetime列格式正确
        if not pd.api.types.is_datetime64_any_dtype(df[datetime_col]):
            df[datetime_col] = pd.to_datetime(df[datetime_col])

        # 重置索引
        df = df.reset_index(drop=True)

        # 创建数据源实例
        return cls(
            dataname=df,
            datetime=datetime_col,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            entry_sig='entry_sig',
            entry_price='entry_price',
            sell_sig='sell_sig',
            sell_price='sell_price'
        )

    def __str__(self) -> str:
        """返回数据源的描述信息"""
        return (
            f"SignalData(records: {len(self.dataname)}, "
            f"period: {self.dataname['datetime'].min()} to {self.dataname['datetime'].max()})"
        )