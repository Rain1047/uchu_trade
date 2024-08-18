from enum import Enum


class EnumSide(Enum):
    BUY = 'buy'  # 买
    SELL = 'sell'  # 卖
    ALL = 'all'  # 买卖都可


class EnumTdMode(Enum):
    # 现货
    CASH = 'cash'  # 非保证金
    # 合约
    ISOLATED = 'isolated'  # 逐仓
    CROSS = 'cross'  # 全仓
    # 现货带单
    SPOT_ISOLATED = 'spot_isolated'  # 现货逐仓(仅适用于现货带单)


class EnumTradeType(Enum):
    PRODUCT = "0"
    DEMO = "1"


class EnumPosSide(Enum):
    LONG = 'long'
    SHORT = 'short'


class EnumOrdType(Enum):
    # place order
    MARKET = "market"  # 市价 市价单，币币和币币杠杆
    LIMIT = "limit"  # 限价


class EnumAlgoOrdType(Enum):
    # place algo order
    CONDITIONAL = 'conditional'  # 单向止盈止损
    OCO = 'oco'  # 双向止盈止损
    TRIGGER = 'trigger'  # 计划委托
    MOVE_ORDER_STOP = 'move_order_stop'  # 移动止盈止损


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


class MethodType(Enum):
    POST = "POST"
    GET = "GET"


class EnumOrderStatus(Enum):
    OPEN = "open"
    CLOSE = "close"


class EnumTpOrdKind(Enum):
    CONDITIONAL = 'conditional'
    LIMIT = "limit"
