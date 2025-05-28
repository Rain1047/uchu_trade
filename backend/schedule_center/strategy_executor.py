import time
from datetime import datetime
import logging
import pandas as pd
from typing import Dict, List, Optional
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord
from backend.strategy_center.atom_strategy.strategy_registry import registry
from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager
from backend.service_center.okx_service.okx_order_service import OKXOrderService
from backend.service_center.okx_service.okx_algo_order_service import OKXAlgoOrderService
from backend.data_object_center.spot_algo_order_record import SpotAlgoOrderRecord

logger = logging.getLogger(__name__)

class StrategyExecutor:
    """策略实盘执行器"""
    
    def __init__(self):
        self.kline_manager = EnhancedKlineManager()
        self.order_service = OKXOrderService()
        self.algo_order_service = OKXAlgoOrderService()
        
    def execute_live_strategy(self, instance_id: int, execution_record_id: int):
        """执行实盘策略"""
        try:
            # 1. 获取策略实例
            instance_dict = StrategyInstance.get_by_id(instance_id)
            if not instance_dict:
                logger.error(f"策略实例 {instance_id} 不存在")
                return False
                
            # 2. 获取策略函数
            entry_strategy = registry.get_strategy(instance_dict['strategy_params']['entry_strategy'])
            exit_strategy = registry.get_strategy(instance_dict['strategy_params']['exit_strategy'])
            filter_strategy = None
            if instance_dict['strategy_params'].get('filter_strategy'):
                filter_strategy = registry.get_strategy(instance_dict['strategy_params']['filter_strategy'])
            
            # 3. 对每个交易对执行策略
            total_trades = 0
            successful_trades = 0
            failed_trades = 0
            total_profit = 0.0
            trade_details = []
            
            for symbol in instance_dict['symbols']:
                try:
                    # 3.1 获取K线数据
                    df = self._get_kline_data(symbol, instance_dict['schedule_frequency'])
                    if df is None or df.empty:
                        logger.warning(f"无法获取 {symbol} 的K线数据")
                        continue
                    
                    # 3.2 检查是否有未完成的订单
                    active_orders = self._get_active_orders(instance_id, symbol)
                    
                    if active_orders:
                        # 3.3 已有持仓，执行出场策略调整止损
                        for order in active_orders:
                            self._adjust_stop_loss(order, df, exit_strategy)
                    else:
                        # 3.4 无持仓，检查入场信号
                        entry_signal = self._check_entry_signal(
                            df, entry_strategy, filter_strategy, instance_dict
                        )
                        
                        if entry_signal:
                            # 3.5 执行入场
                            order_result = self._place_entry_order(
                                symbol, entry_signal, instance_dict
                            )
                            
                            if order_result['success']:
                                total_trades += 1
                                successful_trades += 1
                                trade_details.append({
                                    'symbol': symbol,
                                    'action': 'entry',
                                    'price': order_result['price'],
                                    'size': order_result['size'],
                                    'time': datetime.now().isoformat()
                                })
                            else:
                                failed_trades += 1
                                
                except Exception as e:
                    logger.error(f"处理 {symbol} 时发生错误: {str(e)}")
                    failed_trades += 1
            
            # 4. 更新执行记录
            StrategyExecutionRecord.update_trade_info(
                execution_record_id,
                total_trades=total_trades,
                successful_trades=successful_trades,
                failed_trades=failed_trades,
                total_profit=total_profit,
                profit_rate=total_profit / (instance_dict['entry_per_trans'] or 10000),
                trade_details=trade_details
            )
            
            return True
            
        except Exception as e:
            logger.error(f"执行策略实例 {instance_id} 时发生错误: {str(e)}")
            return False
    
    def _get_kline_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """获取K线数据"""
        try:
            # 转换时间周期格式
            tf_map = {'1h': '1H', '4h': '4H', '1d': '1D', '15m': '15T', '5m': '5T'}
            tf = tf_map.get(timeframe, '4H')
            
            # 获取最新的K线数据
            df = self.kline_manager.get_kline_data(symbol, tf, limit=100)
            return df
            
        except Exception as e:
            logger.error(f"获取 {symbol} K线数据失败: {str(e)}")
            return None
    
    def _get_active_orders(self, instance_id: int, symbol: str) -> List[Dict]:
        """获取活跃订单"""
        try:
            # 从数据库获取该策略实例的活跃订单
            orders = SpotAlgoOrderRecord.get_active_orders_by_strategy(
                strategy_instance_id=instance_id,
                symbol=symbol
            )
            return orders
        except Exception as e:
            logger.error(f"获取活跃订单失败: {str(e)}")
            return []
    
    def _check_entry_signal(self, df: pd.DataFrame, entry_strategy, 
                           filter_strategy, instance_dict: Dict) -> Optional[Dict]:
        """检查入场信号"""
        try:
            # 应用入场策略
            df = entry_strategy(df, None)  # 回测模式
            
            # 应用过滤策略
            if filter_strategy:
                df = filter_strategy(df, None)
            
            # 检查最新的信号
            if len(df) > 0 and df.iloc[-1].get('entry_sig', False):
                return {
                    'price': df.iloc[-1]['entry_price'],
                    'stop_loss': df.iloc[-1].get('stop_loss', df.iloc[-1]['entry_price'] * 0.98),
                    'take_profit': df.iloc[-1].get('take_profit', df.iloc[-1]['entry_price'] * 1.02)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"检查入场信号失败: {str(e)}")
            return None
    
    def _place_entry_order(self, symbol: str, signal: Dict, instance_dict: Dict) -> Dict:
        """下入场订单"""
        try:
            # 计算订单大小
            if instance_dict['entry_per_trans']:
                # 使用固定入场资金
                size = instance_dict['entry_per_trans'] / signal['price']
            else:
                # 使用最大损失计算
                risk = instance_dict['loss_per_trans']
                stop_distance = abs(signal['price'] - signal['stop_loss'])
                size = risk / stop_distance
            
            # 创建止盈止损订单
            order_params = {
                'instId': f"{symbol}-USDT",
                'tdMode': 'cash',
                'side': 'buy',
                'ordType': 'oco',
                'sz': str(size),
                'tpTriggerPx': str(signal['take_profit']),
                'tpOrdPx': '-1',  # 市价
                'slTriggerPx': str(signal['stop_loss']),
                'slOrdPx': '-1'   # 市价
            }
            
            # 下单
            result = self.algo_order_service.place_algo_order(**order_params)
            
            if result and result.get('code') == '0':
                # 保存订单记录
                SpotAlgoOrderRecord.create_from_api_response(
                    result['data'][0],
                    strategy_instance_id=instance_dict['id']
                )
                
                return {
                    'success': True,
                    'price': signal['price'],
                    'size': size,
                    'order_id': result['data'][0]['algoId']
                }
            else:
                return {'success': False, 'error': result.get('msg', '下单失败')}
                
        except Exception as e:
            logger.error(f"下入场订单失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _adjust_stop_loss(self, order: Dict, df: pd.DataFrame, exit_strategy):
        """调整止损"""
        try:
            # 应用出场策略
            df = exit_strategy(df, None)
            
            # 获取新的止损价格
            if len(df) > 0 and 'stop_loss' in df.columns:
                new_stop_loss = df.iloc[-1]['stop_loss']
                
                # 只有当新止损价格更高时才调整（移动止损）
                if new_stop_loss > float(order.get('slTriggerPx', 0)):
                    # 修改订单
                    result = self.algo_order_service.amend_algo_order(
                        algoId=order['algoId'],
                        instId=order['instId'],
                        newSlTriggerPx=str(new_stop_loss)
                    )
                    
                    if result and result.get('code') == '0':
                        logger.info(f"成功调整止损: {order['algoId']} -> {new_stop_loss}")
                    else:
                        logger.error(f"调整止损失败: {result.get('msg', '未知错误')}")
                        
        except Exception as e:
            logger.error(f"调整止损失败: {str(e)}")


# 全局执行器实例
strategy_executor = StrategyExecutor() 