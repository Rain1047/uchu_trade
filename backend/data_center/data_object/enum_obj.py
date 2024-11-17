from enum import Enum
from tvDatafeed import Interval


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
    CONDITIONAL_OCO = 'conditional,oco'


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


class EnumSubType(Enum):
    BUY = ('1', '买入')
    SELL = ('2', '卖出')
    OPEN_LONG = ('3', '开多')
    OPEN_SHORT = ('4', '开空')
    CLOSE_LONG = ('5', '平多')
    CLOSE_SHORT = ('6', '平空')
    FORCE_CLOSE_LONG = ('100', '强减平多')
    FORCE_CLOSE_SHORT = ('101', '强减平空')
    FORCE_BUY = ('102', '强减买入')
    FORCE_SELL = ('103', '强减卖出')
    FORCE_CLOSE = ('104', '强平平多')
    FORCE_CLOSE_SHORT_2 = ('105', '强平平空')
    FORCE_BUY_2 = ('106', '强平买入')
    FORCE_SELL_2 = ('107', '强平卖出')
    FORCE_SWAP_IN = ('110', '强平换币转入')
    FORCE_SWAP_OUT = ('111', '强平换币转出')
    SYSTEM_SWAP_IN = ('118', '系统换币转入')
    SYSTEM_SWAP_OUT = ('119', '系统换币转出')
    AUTO_DECREASE_CLOSE_LONG = ('125', '自动减仓平多')
    AUTO_DECREASE_CLOSE_SHORT = ('126', '自动减仓平空')
    AUTO_DECREASE_BUY = ('127', '自动减仓买入')
    AUTO_DECREASE_SELL = ('128', '自动减仓卖出')
    ONE_CLICK_BORROW_AUTO_BORROW = ('212', '一键借币的自动借币')
    ONE_CLICK_BORROW_AUTO_RETURN = ('213', '一键借币的自动还币')
    BLOCK_TRADE_BUY = ('204', '大宗交易买')
    BLOCK_TRADE_SELL = ('205', '大宗交易卖')
    BLOCK_TRADE_OPEN_LONG = ('206', '大宗交易开多')
    BLOCK_TRADE_OPEN_SHORT = ('207', '大宗交易开空')
    BLOCK_TRADE_CLOSE_LONG = ('208', '大宗交易平多')
    BLOCK_TRADE_CLOSE_SHORT = ('209', '大宗交易平空')
    SPREAD_TRADE_BUY = ('270', '价差交易买')
    SPREAD_TRADE_SELL = ('271', '价差交易卖')
    SPREAD_TRADE_OPEN_LONG = ('272', '价差交易开多')
    SPREAD_TRADE_OPEN_SHORT = ('273', '价差交易开空')
    SPREAD_TRADE_CLOSE_LONG = ('274', '价差交易平多')
    SPREAD_TRADE_CLOSE_SHORT = ('275', '价差交易平空')

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @classmethod
    def get_description(cls, value):
        for item in cls:
            if item.value == value:
                return item.description
        return None


class EnumAutoTradeConfigType(Enum):
    STOP_LOSS = "stop_loss"
    LIMIT_ORDER = "limit_order"


if __name__ == '__main__':
    # 使用示例
    print(EnumSubType.get_description('275'))  # 输出: 价差交易平空
