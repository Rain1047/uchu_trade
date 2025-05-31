from typing import Optional
import pandas as pd
from pandas import DataFrame

from backend.data_object_center.swap_algo_order_record import SwapAlgoOrderRecord
from backend.data_object_center.st_instance import StrategyInstance
from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.strategy_center.atom_strategy.strategy_utils import StrategyUtils
from backend.strategy_center.strategy_processor.strategy_modifier import StrategyModifier
from backend.strategy_center.strategy_result import StrategyExecuteResult


@registry.register(name="dbb_exit_long_strategy", desc="布林带做多止损策略", side="long", type="exit")
def dbb_exit_long_strategy(df: DataFrame, stIns: Optional[StrategyInstance],
                           algoOrdRecord: Optional[SwapAlgoOrderRecord] = None):
    """
    Main entry point for the exit strategy.
    Handles both backtest and live trading modes.
    """
    if stIns is None:
        print("No strategy instance found")
        return dbb_exit_strategy_for_backtest(df)
    return dbb_exit_strategy_for_live(df=df, algoOrdRecord=algoOrdRecord)


def dbb_exit_strategy_for_live(df: DataFrame, algoOrdRecord: Optional[SwapAlgoOrderRecord] = None) \
        -> StrategyExecuteResult:
    """
    Live trading implementation of the exit strategy.
    Args:
        df: DataFrame containing price and indicator data
        algoOrdRecord: The algorithm order record containing order information
    Returns:
        StrategyExecuteResult: Contains exit strategy decisions
    """
    strategy_execute_result = StrategyExecuteResult()

    # Convert order creation time to datetime if needed
    ord_create_time = pd.to_datetime(algoOrdRecord.create_time)

    # Find the index in DataFrame corresponding to order creation time
    start_index = StrategyUtils.find_kline_index_by_time(df, ord_create_time)
    if start_index is None:
        return strategy_execute_result

    # Get the latest index
    end_index = df.index[-1]

    # Check if any close price exceeded upper_band2 between order creation and now
    slice_df = df.loc[start_index:end_index]
    exceeded_upper_band2 = (slice_df['close'] > slice_df['upper_band2']).any()

    # 获取当前止损价
    current_stop_loss = float(algoOrdRecord.sl_trigger_px) if algoOrdRecord.sl_trigger_px else 0
    current_sma20 = df.iloc[-1]['sma20']

    if exceeded_upper_band2:
        # 如果突破过第二层布林带，使用第一层布林带上轨作为止损
        exit_price = df.iloc[-1]['upper_band1']
        print("Exit price (upper_band1):", exit_price)
    else:
        # 如果没有突破过第二层布林带，只有当MA20升高时才更新止损价
        if current_sma20 > current_stop_loss:
            exit_price = current_sma20
            print("Exit price (new MA20):", exit_price)
        else:
            exit_price = current_stop_loss
            print("Exit price (previous stop loss):", exit_price)

    strategy_execute_result.stop_loss_price = exit_price
    strategy_execute_result.exit_price = exit_price

    return strategy_execute_result


def dbb_exit_strategy_for_backtest(df: DataFrame) -> DataFrame:
    """
    Backtest implementation of the exit strategy.
    """
    if df.empty:
        return df

    # 若缺指标列，先计算
    if 'sma20' not in df.columns:
        df['sma20'] = df['close'].rolling(window=20).mean()
    if 'upper_band1' not in df.columns or 'upper_band2' not in df.columns:
        sma20 = df['close'].rolling(window=20).mean()
        std20 = df['close'].rolling(window=20).std()
        df['upper_band1'] = sma20 + std20 * 2
        df['upper_band2'] = sma20 + std20 * 3

    df['sell_sig'] = 0
    df['sell_price'] = df['sma20']
    df['prev_sell_price'] = df['sell_price'].shift(1)  # 添加上一期的止损价

    for i in range(1, len(df)):
        if df.iloc[:i]['entry_sig'].sum() == 0:
            continue

        last_buy_idx = df.iloc[:i][df.iloc[:i]['entry_sig'] == 1].index[-1]
        segment = df.loc[last_buy_idx:df.index[i]]

        if segment['sell_sig'].sum() > 0:
            continue

        if (segment['close'] > segment['upper_band2']).any():
            # 如果突破过第二层布林带，使用第一层布林带上轨作为止损
            df.loc[df.index[i], 'sell_price'] = df.loc[df.index[i - 1], 'upper_band1']
        else:
            # 如果没有突破过第二层布林带，只有当MA20升高时才更新止损价
            current_sma20 = df.loc[df.index[i], 'sma20']
            prev_sell_price = df.loc[df.index[i], 'prev_sell_price']
            
            if current_sma20 > prev_sell_price:
                df.loc[df.index[i], 'sell_price'] = current_sma20
            else:
                df.loc[df.index[i], 'sell_price'] = prev_sell_price

        current_close = df.loc[df.index[i], 'close']
        current_sell_price = df.loc[df.index[i], 'sell_price']

        if pd.notna(current_sell_price):
            df.loc[df.index[i], 'sell_sig'] = 1 if current_close < current_sell_price else 0

    # 删除临时列
    df.drop('prev_sell_price', axis=1, inplace=True)
    return df


if __name__ == '__main__':
    strategy_modifier = StrategyModifier()
    # strategy_modifier.main_task()
    st_inst = StrategyInstance.get_st_instance_by_id(id=10)
    algo_ord = SwapAlgoOrderRecord.get_by_id(record_id=4)
    df = strategy_modifier.get_data_frame(st_inst)
    strategy_execute_result = dbb_exit_strategy_for_live(df, algo_ord)

    print(strategy_execute_result.to_dict())
