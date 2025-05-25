
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class Strategy股票魔法师2 电子书:
    """
    基于《股票魔法师2 电子书》提取的交易策略
    
    来源: 股票魔法师2 电子书
    时间框架: short
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.name = "strategy_股票魔法师2 电子书"
        self.timeframe = "short"
        self.parameters = parameters or {
        "risk_percent": 2.0,
        "max_position_size": 0.2,
        "stop_loss_percent": 5.0,
        "take_profit_percent": 10.0,
        "numeric_values": [
                978.0,
                996307932.0,
                2017.0,
                2018.0,
                1.0
        ],
        "percentages": [
                100.0,
                100.0,
                160.0,
                90.0,
                50.0,
                7.0,
                20.0
        ]
}
        
        # 策略状态
        self.position = 0  # 0: 空仓, 1: 多头, -1: 空头
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
        
    def check_entry_conditions(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """检查入场条件"""
        if current_index < 50:  # 确保有足够的历史数据
            return {"signal": "no_action", "reason": "insufficient_data"}
        
        current_row = df.iloc[current_index]
        
        # 入场条件检查

        # 入场规则_1
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_1"
            }


        # 入场规则_1
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_1"
            }


        # 入场规则_1
        if current_price > df.iloc[current_index-1]['high'] and current_price > df.iloc[current_index-1]['high'] and current_price > df.iloc[current_index-1]['high']:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_1"
            }


        # 入场规则_2
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_2"
            }


        # 入场规则_1
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_1"
            }


        # 入场规则_1
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_1"
            }


        # 入场规则_2
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_2"
            }


        # 入场规则_1
        if False:
            # 设置止损和止盈
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.1
            
            return {
                "signal": "buy",
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": "入场规则_1"
            }

        
        return {"signal": "no_action", "reason": "conditions_not_met"}
    
    def check_exit_conditions(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """检查出场条件"""
        if self.position == 0:
            return {"signal": "no_action", "reason": "no_position"}
        
        current_row = df.iloc[current_index]
        current_price = current_row['close']
        
        # 止损检查
        if self.stop_loss_price and current_price <= self.stop_loss_price:
            return {"signal": "exit", "reason": "stop_loss", "price": current_price}
        
        # 止盈检查
        if self.take_profit_price and current_price >= self.take_profit_price:
            return {"signal": "exit", "reason": "take_profit", "price": current_price}
        
        # 其他出场条件

        
        return {"signal": "no_action", "reason": "hold_position"}
    
    def calculate_position_size(self, account_balance: float, risk_percent: float = 2.0) -> float:
        """计算仓位大小"""
        risk_amount = account_balance * (risk_percent / 100)
        if self.entry_price and self.stop_loss_price:
            risk_per_share = abs(self.entry_price - self.stop_loss_price)
            if risk_per_share > 0:
                return risk_amount / risk_per_share
        return account_balance * 0.1  # 默认10%仓位
    
    def execute_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行策略"""
        signals = []
        
        for i in range(len(df)):
            if self.position == 0:
                # 检查入场条件
                entry_signal = self.check_entry_conditions(df, i)
                if entry_signal["signal"] == "buy":
                    self.position = 1
                    self.entry_price = entry_signal["price"]
                    self.stop_loss_price = entry_signal.get("stop_loss")
                    self.take_profit_price = entry_signal.get("take_profit")
                    signals.append({"index": i, "signal": "buy", "price": self.entry_price})
                elif entry_signal["signal"] == "sell":
                    self.position = -1
                    self.entry_price = entry_signal["price"]
                    self.stop_loss_price = entry_signal.get("stop_loss")
                    self.take_profit_price = entry_signal.get("take_profit")
                    signals.append({"index": i, "signal": "sell", "price": self.entry_price})
            else:
                # 检查出场条件
                exit_signal = self.check_exit_conditions(df, i)
                if exit_signal["signal"] == "exit":
                    signals.append({"index": i, "signal": "exit", "price": exit_signal["price"]})
                    self.position = 0
                    self.entry_price = None
                    self.stop_loss_price = None
                    self.take_profit_price = None
        
        # 将信号添加到DataFrame
        df_copy = df.copy()
        df_copy['signal'] = 'hold'
        df_copy['signal_price'] = np.nan
        
        for signal in signals:
            df_copy.loc[signal["index"], 'signal'] = signal["signal"]
            df_copy.loc[signal["index"], 'signal_price'] = signal["price"]
        
        return df_copy
