from enum import Enum


class EnumSide(Enum):
    BUY = 'buy'  # 买
    SELL = 'sell'  # 卖
    ALL = 'all'  # 买卖都可


class EnumTdMode(Enum):
    ISOLATED = 'isolated'  # 逐仓
    CROSS = 'cross'  # 全仓
    CASH = 'cash'  # 非保证金
    SPOT_ISOLATED = 'spot_isolated'  # 现货逐仓(仅适用于现货带单)


class EnumTradeType(Enum):
    PRODUCT = "0"
    DEMO = "1"


class EnumPosSide(Enum):
    LONG = 'long'
    SHORT = 'short'


class EnumOrdType(Enum):
    MARKET = "market"
    CONDITIONAL = 'conditional'
    OCO = 'oco'
    TRIGGER = 'trigger'
    MOVE_ORDER_STOP = 'move_order_stop'
    TWAP = 'twap'


class EnumTriggerPxType(Enum):
    LAST = 'last'  # 最新价格 default
    INDEX = 'index'  # 指数价格
    MARK = 'mark'  # 标记价格


class EnumUnit(Enum):
    USDS = "usds"


class EnumTradeEnv(Enum):
    DEMO = "demo"
    MARKET = "market"


class EnumTimeFrame(Enum):
    D1_L = "1d"
    D1_U = "1D"
    H4_U = "4H"
    H4_L = "4h"


class EnumInstanceType(Enum):
    SPOT = "SPOT"


class EnumOperationMode(Enum):
    MANUAL = "manual"
    AUTO = "auto"


class EnumPurchaseRedempt(Enum):
    PURCHASE = "purchase"
    REDEMPT = "redempt"
