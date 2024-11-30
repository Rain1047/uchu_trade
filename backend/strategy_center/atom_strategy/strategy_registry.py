from typing import Callable, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class StrategyRegistry:
    _strategies: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func):
            cls._strategies[name] = func
            return func

        return decorator

    @classmethod
    def get_strategy(cls, name: str) -> Callable:
        if name not in cls._strategies:
            raise KeyError(f"Strategy {name} not found")
        return cls._strategies[name]

    @classmethod
    def execute_strategy(cls, df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
        try:
            strategy = cls.get_strategy(strategy_name)
            return strategy(df)
        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}")
            raise
