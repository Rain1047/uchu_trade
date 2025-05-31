from datetime import datetime
from typing import Optional, Dict, List
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from backend._utils import DatabaseUtils, LogConfig

Base = declarative_base()
logger = LogConfig.get_logger(__name__)

class EnhancedBacktestRecord(Base):
    """增强回测记录"""
    __tablename__ = 'enhanced_backtest_records'
    
    id = Column(Integer, primary_key=True)
    entry_strategy = Column(String(100), nullable=False)
    exit_strategy = Column(String(100), nullable=False)
    filter_strategy = Column(String(100))
    symbols = Column(JSON, nullable=False)
    timeframe = Column(String(10), nullable=False)
    initial_cash = Column(Float, nullable=False)
    risk_percent = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    start_date = Column(String(10))
    end_date = Column(String(10))
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    error_message = Column(String(500))
    description = Column(String(500))
    
    # 回测统计字段
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    avg_win_profit = Column(Float, default=0.0)
    avg_loss_profit = Column(Float, default=0.0)
    profit_loss_ratio = Column(Float, default=0.0)
    backtest_period = Column(String(10), default='1m')  # 添加回测周期字段
    
    def __init__(self,
                 entry_strategy: str,
                 exit_strategy: str,
                 filter_strategy: Optional[str],
                 symbols: List[str],
                 timeframe: str,
                 initial_cash: float,
                 risk_percent: float,
                 commission: float,
                 start_date: Optional[str],
                 end_date: Optional[str],
                 status: str,
                 start_time: datetime,
                 end_time: Optional[datetime] = None,
                 error_message: Optional[str] = None,
                 description: str = "增强回测",
                 backtest_period: str = "1m"):
        self.entry_strategy = entry_strategy
        self.exit_strategy = exit_strategy
        self.filter_strategy = filter_strategy
        self.symbols = symbols
        self.timeframe = timeframe
        self.initial_cash = initial_cash
        self.risk_percent = risk_percent
        self.commission = commission
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.error_message = error_message
        self.description = description
        self.backtest_period = backtest_period
        # 初始化统计字段
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.win_rate = 0.0
        self.total_return = 0.0
        self.avg_win_profit = 0.0
        self.avg_loss_profit = 0.0
        self.profit_loss_ratio = 0.0
    
    @classmethod
    def create(cls, data: Dict, db: Session) -> 'EnhancedBacktestRecord':
        """创建回测记录"""
        try:
            record = cls(
                entry_strategy=data['entry_strategy'],
                exit_strategy=data['exit_strategy'],
                filter_strategy=data.get('filter_strategy'),
                symbols=data['symbols'],
                timeframe=data['timeframe'],
                initial_cash=data['initial_cash'],
                risk_percent=data['risk_percent'],
                commission=data['commission'],
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                status='running',
                start_time=datetime.now(),
                description=data.get('description', '增强回测'),
                backtest_period=data.get('backtest_period', '1m')
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except Exception as e:
            db.rollback()
            logger.error(f"创建回测记录失败: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id: int, db: Optional[Session] = None) -> Optional['EnhancedBacktestRecord']:
        """根据ID获取回测记录。如果未提供 db，则自动获取一个新的 session。"""
        external_db = db is not None
        if db is None:
            db = DatabaseUtils.get_db_session()
        try:
            return db.query(cls).filter(cls.id == id).first()
        except Exception as e:
            logger.error(f"获取回测记录失败: {e}")
            return None
        finally:
            if not external_db:
                db.close()
    
    def save(self, db: Session):
        """保存回测记录"""
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
        except Exception as e:
            db.rollback()
            logger.error(f"保存回测记录失败: {e}")
            raise
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'entry_strategy': self.entry_strategy,
            'exit_strategy': self.exit_strategy,
            'filter_strategy': self.filter_strategy,
            'symbols': self.symbols,
            'timeframe': self.timeframe,
            'initial_cash': self.initial_cash,
            'risk_percent': self.risk_percent,
            'commission': self.commission,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message,
            'description': self.description,
            'backtest_period': self.backtest_period,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'total_return': self.total_return,
            'avg_win_profit': self.avg_win_profit,
            'avg_loss_profit': self.avg_loss_profit,
            'profit_loss_ratio': self.profit_loss_ratio
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict())

    @classmethod
    def list_all(cls, status: Optional[str] = None, limit: int = 100) -> List['EnhancedBacktestRecord']:
        """获取所有记录"""
        db = DatabaseUtils.get_db_session()
        try:
            query = db.query(cls)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.start_time.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"获取回测记录列表失败: {e}")
            return []
        finally:
            db.close()

    @classmethod
    def update_status(cls, record_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """更新状态"""
        db = DatabaseUtils.get_db_session()
        try:
            record = db.query(cls).filter(cls.id == record_id).first()
            if record:
                record.status = status
                record.error_message = error_message
                record.end_time = datetime.now() if status == 'completed' or status == 'failed' else None
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"更新回测状态失败: {e}")
            return False
        finally:
            db.close()

    @classmethod
    def update_results(cls, record_id: int, results: Dict) -> bool:
        """更新回测结果"""
        db = DatabaseUtils.get_db_session()
        try:
            record = db.query(cls).filter(cls.id == record_id).first()
            if record:
                # 更新整体统计
                if 'total_trades' in results:
                    record.total_trades = results['total_trades']
                if 'winning_trades' in results:
                    record.winning_trades = results['winning_trades']
                if 'losing_trades' in results:
                    record.losing_trades = results['losing_trades']
                if 'win_rate' in results:
                    record.win_rate = results['win_rate']
                if 'total_return' in results:
                    record.total_return = results['total_return']
                if 'avg_win_profit' in results:
                    record.avg_win_profit = results['avg_win_profit']
                if 'avg_loss_profit' in results:
                    record.avg_loss_profit = results['avg_loss_profit']
                if 'profit_loss_ratio' in results:
                    record.profit_loss_ratio = results['profit_loss_ratio']
                if 'symbol_results' in results and hasattr(record, 'symbol_results'):
                    record.symbol_results = results['symbol_results']
                
                record.end_time = datetime.now() if results['status'] == 'completed' or results['status'] == 'failed' else None
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"更新回测结果失败: {e}")
            return False
        finally:
            db.close()

    @classmethod
    def delete_by_id(cls, record_id: int) -> bool:
        """删除记录"""
        db = DatabaseUtils.get_db_session()
        try:
            record = db.query(cls).filter(cls.id == record_id).first()
            if record:
                db.delete(record)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"删除回测记录失败: {e}")
            return False
        finally:
            db.close()

    @classmethod
    def get_summary_stats(cls) -> Dict:
        """获取汇总统计"""
        db = DatabaseUtils.get_db_session()
        try:
            total_count = db.query(cls).count()
            running_count = db.query(cls).filter(cls.status == 'running').count()
            completed_count = db.query(cls).filter(cls.status == 'completed').count()
            failed_count = db.query(cls).filter(cls.status == 'failed').count()
            
            # 获取盈利策略数
            profitable_count = db.query(cls).filter(
                cls.status == 'completed',
                cls.total_return > 0
            ).count()
            
            # 获取最高胜率
            max_win_rate_record = db.query(cls).filter(
                cls.status == 'completed'
            ).order_by(cls.win_rate.desc()).first()
            
            max_win_rate = max_win_rate_record.win_rate if max_win_rate_record else 0.0
            
            return {
                'total_count': total_count,
                'running_count': running_count,
                'completed_count': completed_count,
                'failed_count': failed_count,
                'profitable_count': profitable_count,
                'max_win_rate': max_win_rate
            }
        except Exception as e:
            logger.error(f"获取汇总统计失败: {e}")
            return {
                'total_count': 0,
                'running_count': 0,
                'completed_count': 0,
                'failed_count': 0,
                'profitable_count': 0,
                'max_win_rate': 0.0
            }
        finally:
            db.close() 