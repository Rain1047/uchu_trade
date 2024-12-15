import pandas as pd


class StrategyUtils:
    @staticmethod
    def find_kline_index_by_time(df: pd.DataFrame, target_time):
        """
        Find the index of the corresponding kline period for a given timestamp

        Args:
            df: DataFrame with datetime index
            target_time: timestamp to look up (str or datetime)

        Returns:
            int: index of the corresponding kline period
        """
        # Convert target_time to datetime if it's string
        if isinstance(target_time, str):
            target_time = pd.to_datetime(target_time)

        # Convert datetime column to datetime type if it's not already
        if df['datetime'].dtype != 'datetime64[ns]':
            df['datetime'] = pd.to_datetime(df['datetime'])

        # Get the datetime that's less than or equal to target_time
        mask = df['datetime'] <= target_time
        if not mask.any():
            return None  # Target time is before any kline period

        return df[mask].index[-1]