from abc import ABC, abstractmethod


# 订单处理策略接口
class OrderProcessor(ABC):
    @abstractmethod
    def process(self, order: dict) -> bool:
        pass
