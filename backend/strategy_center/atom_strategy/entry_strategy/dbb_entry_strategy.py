import os
import sys
from typing import Optional
import pandas as pd
from backend.object_center._object_dao.st_instance import StrategyInstance
from backend.service.okx_service.ticker_price_service import TickerPriceCollector
from backend.object_center.enum_obj import EnumTradeType, EnumSide, EnumPosSide
from backend.strategy_center.strategy_result import StrategyExecuteResult
from backend.data_center.kline_data.kline_data_collector import KlineDataCollector
from backend.strategy_center.atom_strategy.strategy_registry import registry

# 将项目根目录添加到Python解释器的搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import okx.PublicData as PublicData
import okx.MarketData as MarketData
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper

marketDataAPI = MarketData.MarketAPI(flag=EnumTradeType.PRODUCT.value)
publicDataAPI = PublicData.PublicAPI(flag=EnumTradeType.PRODUCT.value)
okx = OKXAPIWrapper()
price_collector = TickerPriceCollector()
tv = KlineDataCollector()


@registry.register(name="dbb_entry_long_strategy", desc="布林带入场策略", side="long", type="entry")
def dbb_entry_long_strategy(df: pd.DataFrame, stIns: Optional[StrategyInstance]):
    if stIns is None:
        return dbb_entry_long_strategy_backtest(df)
    else:
        return dbb_entry_long_strategy_live(df, stIns)


# @registry.register(name="dbb_entry_long_strategy_backtest", desc="布林带入场策略", side="long")
def dbb_entry_long_strategy_backtest(df: pd.DataFrame):
    # Initialize buy_sig column with zeros
    df['entry_sig'] = 0
    df['entry_price'] = 0
    df['prev_open_1'] = df['open'].shift(1)
    df['prev_upper_band1_1'] = df['upper_band1'].shift(1)
    # Create conditions for current row
    current_condition = (
            (df['open'] < df['upper_band1'])  # 条件1
            & (df['close'] > df['upper_band1'])  # 条件2
            & (df['prev_open_1'] < df['prev_upper_band1_1'])  # 条件3
    )

    # 添加调试信息
    df['debug_condition1'] = df['open'] < df['upper_band1']
    df['debug_condition2'] = df['close'] > df['upper_band1']
    df['debug_condition3'] = df['prev_open_1'] < df['prev_upper_band1_1']

    # Set buy signals
    df.loc[current_condition, 'entry_sig'] = 1
    df.loc[current_condition, 'entry_price'] = df.loc[current_condition, 'close']
    # Clean up temporary columns
    df.drop(['prev_open_1', 'prev_upper_band1_1',
             'debug_condition1', 'debug_condition2',
             'debug_condition3'], axis=1, inplace=True)

    return df


# @registry.register(name="dbb_entry_long_strategy_live", desc="布林带入场策略", side="long")
def dbb_entry_long_strategy_live(df: pd.DataFrame, stIns: StrategyInstance) -> StrategyExecuteResult:
    res = StrategyExecuteResult()
    if not df.empty:
        df['signal'] = 'no_sig'
        if ((df.iloc[-2]['close'] > df.iloc[-2]['upper_band1']) and
                (df.iloc[-3]['close'] < df.iloc[-3]['upper_band1']) and
                (df.iloc[-4]['close'] < df.iloc[-4]['upper_band1'])):
            df.loc[df.index[-1], 'signal'] = EnumSide.BUY.value
        # 如果满足买入信号，则设置交易信号为True
        if df.iloc[-1]['signal'] == EnumSide.BUY.value:
            # 获取仓位
            position = str(
                stIns.loss_per_trans * round(df.iloc[-1]['close'] / (df.iloc[-1]['close'] - df.iloc[-1]['sma20']),
                                             2) * 10)
            # 获取单个产品行情信息
            res.sz = price_collector.get_sz(instId=stIns.trade_pair, position=position)
            res.signal = True
            res.side = EnumSide.BUY.value
            res.pos_side = EnumPosSide.LONG.value
            res.exit_price = str(df.iloc[-2]['sma20'])
            res.interval = stIns.time_frame
            res.st_inst_id = stIns.id
            print(f"dbb_entry_long_strategy_live#execute result: {stIns.trade_pair} position is: {position}")
            return res
        else:
            print("dbb_entry_long_strategy_live#execute result: no signal")
            res.signal = False
            return res


if __name__ == '__main__':
    print(registry.list_strategies())
