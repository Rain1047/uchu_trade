"""
测试实盘策略执行链路
"""
import asyncio
import logging
from datetime import datetime
from backend.schedule_center.strategy_executor import strategy_executor
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_strategy_execution():
    """测试策略执行"""
    try:
        # 1. 创建测试策略实例
        test_instance = StrategyInstance.create(
            strategy_id='test_live_strategy',
            strategy_name='测试实盘策略',
            strategy_type='combination',
            strategy_params={
                'entry_strategy': 'dbb_entry_long_strategy',
                'exit_strategy': 'dbb_exit_long_strategy',
                'filter_strategy': 'sma_perfect_order_filter_strategy'
            },
            schedule_frequency='4h',  # 4小时频率，使用已有数据
            symbols=['BTC', 'ETH'],  # 测试交易对
            entry_per_trans=100.0,  # 每笔100 USDT
            commission=0.001
        )
        
        if not test_instance:
            logger.error("创建测试实例失败")
            return
        
        instance_id = test_instance['id']
        logger.info(f"创建测试实例成功: {instance_id}")
        
        # 2. 创建执行记录
        execution_record = StrategyExecutionRecord.create(
            instance_id=instance_id,
            status='running'
        )
        
        if not execution_record:
            logger.error("创建执行记录失败")
            return
        
        record_id = execution_record['id']
        logger.info(f"创建执行记录成功: {record_id}")
        
        # 3. 执行策略
        logger.info("开始执行策略...")
        success = strategy_executor.execute_live_strategy(instance_id, record_id)
        
        if success:
            logger.info("策略执行成功!")
            
            # 4. 查看执行结果
            updated_record = StrategyExecutionRecord.get_by_id(record_id)
            if updated_record:
                logger.info(f"执行结果:")
                logger.info(f"  - 总交易次数: {updated_record.get('total_trades', 0)}")
                logger.info(f"  - 成功交易: {updated_record.get('successful_trades', 0)}")
                logger.info(f"  - 失败交易: {updated_record.get('failed_trades', 0)}")
                logger.info(f"  - 总收益: {updated_record.get('total_profit', 0)}")
                logger.info(f"  - 交易详情: {updated_record.get('trade_details', [])}")
        else:
            logger.error("策略执行失败!")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_mock_execution():
    """测试模拟执行（不真实下单）"""
    try:
        logger.info("="*50)
        logger.info("测试模拟执行流程")
        logger.info("="*50)
        
        # 模拟获取K线数据
        from backend.data_center.kline_data.enhanced_kline_manager import EnhancedKlineManager
        kline_manager = EnhancedKlineManager()
        
        # 测试获取BTC的K线数据
        df = kline_manager.get_kline_data('BTC', '4h', limit=100)  # 使用4h数据
        if df is not None and not df.empty:
            logger.info(f"成功获取BTC K线数据: {len(df)} 条")
            logger.info(f"最新K线: {df.iloc[-1].to_dict()}")
        else:
            logger.warning("无法获取K线数据")
        
        # 测试策略信号
        from backend.strategy_center.atom_strategy.strategy_registry import registry
        
        # 获取策略
        entry_strategy = registry.get_strategy('dbb_entry_long_strategy')
        exit_strategy = registry.get_strategy('dbb_exit_long_strategy')
        filter_strategy = registry.get_strategy('sma_perfect_order_filter_strategy')
        
        if entry_strategy and df is not None:
            # 应用策略
            df = entry_strategy(df, None)
            if filter_strategy:
                df = filter_strategy(df, None)
            
            # 检查信号
            if 'entry_sig' in df.columns and df.iloc[-1]['entry_sig']:
                logger.info("发现入场信号!")
                logger.info(f"  - 入场价格: {df.iloc[-1].get('entry_price', 'N/A')}")
                logger.info(f"  - 止损价格: {df.iloc[-1].get('stop_loss', 'N/A')}")
            else:
                logger.info("未发现入场信号")
                
    except Exception as e:
        logger.error(f"模拟测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("实盘策略执行测试")
    print("="*60 + "\n")
    
    print("选择测试模式:")
    print("1. 模拟执行（不真实下单）")
    print("2. 真实执行（会调用OKX API）")
    
    choice = input("\n请输入选择 (1 或 2): ")
    
    if choice == '1':
        test_mock_execution()
    elif choice == '2':
        confirm = input("\n警告: 这将执行真实交易！确认继续？(yes/no): ")
        if confirm.lower() == 'yes':
            test_strategy_execution()
        else:
            print("已取消")
    else:
        print("无效选择") 