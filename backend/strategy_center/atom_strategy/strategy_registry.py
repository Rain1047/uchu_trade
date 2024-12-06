import importlib
import inspect
import os
from typing import Callable, Dict, Optional, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class StrategyRegistry:
    _instance = None
    _strategies: Dict[str, Callable] = {}
    _strategies_config: List[Dict[str, str]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 获取 atom_strategy 目录的绝对路径
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            strategy_dir = os.path.join(base_path, 'strategy_center', 'atom_strategy')
            cls._instance._load_strategies(strategy_dir)
        return cls._instance

    def _load_strategies(self, directory: str):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    self._load_module(file_path)

    def _load_module(self, file_path: str):
        try:
            module_name = os.path.basename(file_path)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj):
                        if hasattr(obj, '_strategy_name'):
                            self._strategies[obj._strategy_name] = obj
                            logger.info(f"Loaded strategy: {obj._strategy_name} from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {str(e)}")

    @classmethod
    def register(cls, name: str, desc: str, type: str, side: str):
        def decorator(func):
            cls._strategies[name] = func
            cls._strategies_config.append(
                {
                    "name": name,
                    "desc": desc,
                    "side": side,
                    "type": type
                }
            )
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

    @classmethod
    def _auto_register_strategies(cls):
        for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(func, 'strategy_name'):
                cls._strategies[func.strategy_name] = func
                logger.info(f"Automatically registered strategy: {func.strategy_name}")

    @classmethod
    def print_registered_strategies(cls):
        if cls._strategies:
            print("Registered strategies:")
            for name in cls._strategies:
                print(f"- {name}")
        else:
            print("No strategies registered")

    def list_strategies(self) -> list:
        return self._strategies_config


registry = StrategyRegistry()

# 确保在导入其他模块前先创建实例
from backend.strategy_center.atom_strategy.entry_strategy.dbb_entry_strategy import *
from backend.strategy_center.atom_strategy.exit_strategy.dbb_exit_strategy import *
from backend.strategy_center.atom_strategy.filter_strategy.sma_diff_increasing_filter_strategy import *
from backend.strategy_center.atom_strategy.filter_strategy.sma_perfect_order_filter_strategy import *


if __name__ == '__main__':
    # registry = StrategyRegistry(directory='backend/strategy_center/atom_strategy')
    print(registry.list_strategies())
