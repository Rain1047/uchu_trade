from backend.data_object_center.base import Base, engine, Session
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.data_object_center.backtest_result import BacktestResult
from backend.data_object_center.backtest_record import BacktestRecord

def init_db():
    """初始化数据库，创建所有表"""
    # 创建所有表
    Base.metadata.create_all(engine)
    
    # 添加测试数据
    session = Session()
    try:
        # 检查是否已有数据
        if session.query(StrategyInstance).count() == 0:
            # 添加测试策略
            test_strategy = StrategyInstance(
                strategy_id="ST1",
                strategy_name="布林带策略",
                strategy_type="bollinger",
                strategy_params={
                    "period": 20,
                    "devfactor": 2,
                    "entry_threshold": 0.02,
                    "exit_threshold": 0.01
                }
            )
            session.add(test_strategy)
            
            # 添加另一个测试策略
            test_strategy2 = StrategyInstance(
                strategy_id="ST2",
                strategy_name="均线交叉策略",
                strategy_type="ma_cross",
                strategy_params={
                    "fast_period": 5,
                    "slow_period": 20,
                    "entry_threshold": 0.01,
                    "exit_threshold": 0.005
                }
            )
            session.add(test_strategy2)
            
            session.commit()
            print("测试数据添加成功")
    except Exception as e:
        session.rollback()
        print(f"添加测试数据失败: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    init_db() 