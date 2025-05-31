from typing import Optional
import pandas as pd

class BacktestSystem:
    def __init__(self, data, signals, initial_cash, risk_percent, commission):
        self.data = data
        self.signals = signals
        self.initial_cash = initial_cash
        self.risk_percent = risk_percent
        self.commission = commission

    def run(self) -> Optional[BacktestResult]:
        """运行回测"""
        try:
            logger.info("🚀 开始回测")
            
            # 初始化结果
            self.trades = []
            self.positions = {}
            self.cash = self.initial_cash
            self.equity_curve = []
            
            # 遍历每个时间点
            for i in range(len(self.data)):
                current_time = self.data.index[i]
                current_price = self.data['close'].iloc[i]
                
                # 更新持仓
                self._update_positions(current_time, current_price)
                
                # 检查出场信号
                if self.signals['exit'].iloc[i]:
                    self._close_all_positions(current_time, current_price)
                
                # 检查入场信号
                if self.signals['entry'].iloc[i] and self.signals['filter'].iloc[i]:
                    self._open_position(current_time, current_price)
                
                # 记录权益
                self.equity_curve.append({
                    'time': current_time,
                    'equity': self._calculate_equity(current_price)
                })
            
            # 生成回测结果
            if self.trades:
                result = self._generate_result()
                logger.info("✅ 回测完成")
                return result
            else:
                logger.warning("❌ 没有交易记录")
                return None
            
        except Exception as e:
            logger.error(f"回测执行出错: {str(e)}")
            return None

    def _update_positions(self, current_time: pd.Timestamp, current_price: float):
        """更新持仓状态"""
        for symbol, position in list(self.positions.items()):
            # 更新持仓市值
            position['current_value'] = position['size'] * current_price
            
            # 更新浮动盈亏
            position['unrealized_pnl'] = position['current_value'] - position['cost']
            
            # 更新持仓时间
            position['holding_time'] = (current_time - position['entry_time']).total_seconds() / 3600  # 小时

    def _close_all_positions(self, current_time: pd.Timestamp, current_price: float):
        """平掉所有持仓"""
        for symbol, position in list(self.positions.items()):
            # 计算交易成本
            cost = position['size'] * current_price * self.commission
            
            # 更新现金
            self.cash += position['current_value'] - cost
            
            # 记录交易
            self.trades.append({
                'symbol': symbol,
                'entry_time': position['entry_time'],
                'exit_time': current_time,
                'entry_price': position['entry_price'],
                'exit_price': current_price,
                'size': position['size'],
                'pnl': position['unrealized_pnl'] - cost,
                'holding_time': position['holding_time']
            })
            
            # 移除持仓
            del self.positions[symbol]

    def _open_position(self, current_time: pd.Timestamp, current_price: float):
        """开仓"""
        # 计算仓位大小
        risk_amount = self.cash * self.risk_percent / 100
        position_size = risk_amount / current_price
        
        # 计算交易成本
        cost = position_size * current_price * self.commission
        
        # 检查资金是否足够
        if cost > self.cash:
            return
        
        # 更新现金
        self.cash -= cost
        
        # 记录持仓
        self.positions['BTC'] = {
            'size': position_size,
            'entry_price': current_price,
            'entry_time': current_time,
            'cost': cost,
            'current_value': position_size * current_price,
            'unrealized_pnl': 0,
            'holding_time': 0
        }

    def _calculate_equity(self, current_price: float) -> float:
        """计算当前权益"""
        equity = self.cash
        for position in self.positions.values():
            equity += position['current_value']
        return equity

    def _generate_result(self) -> BacktestResult:
        """生成回测结果"""
        # 计算统计数据
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])
        losing_trades = len([t for t in self.trades if t['pnl'] <= 0])
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        winning_pnl = sum(t['pnl'] for t in self.trades if t['pnl'] > 0)
        losing_pnl = sum(t['pnl'] for t in self.trades if t['pnl'] <= 0)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else float('inf')
        
        # 计算最大回撤
        max_drawdown = 0
        peak = self.equity_curve[0]['equity']
        for point in self.equity_curve:
            if point['equity'] > peak:
                peak = point['equity']
            drawdown = (peak - point['equity']) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            total_pnl=total_pnl,
            winning_pnl=winning_pnl,
            losing_pnl=losing_pnl,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            trades=self.trades,
            equity_curve=self.equity_curve
        ) 