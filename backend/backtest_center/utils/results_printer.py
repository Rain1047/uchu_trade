import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging
from models.backtest_results import BacktestResults
from models.trade_record import TradeRecord

logger = logging.getLogger(__name__)


class ResultsPrinter:
    """结果打印和导出工具类"""

    @staticmethod
    def print_results(results: BacktestResults) -> None:
        """
        打印回测结果

        Args:
            results: 回测结果对象
        """
        logger.info(str(results))

    @staticmethod
    def export_trade_records(
            records: List[TradeRecord],
            stats: Dict[str, Any],
            output_dir: str = "results"
    ) -> None:
        """
        导出交易记录和统计数据到Excel

        Args:
            records: 交易记录列表
            stats: 统计数据字典
            output_dir: 输出目录
        """
        try:
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 转换交易记录为DataFrame
            records_df = pd.DataFrame([record.to_dict() for record in records])

            # 添加累计收益列
            if not records_df.empty:
                records_df['cumulative_pnl'] = records_df['pnl'].cumsum()

            # 创建统计数据DataFrame
            stats_df = pd.DataFrame([stats])

            # 导出到Excel
            with pd.ExcelWriter(output_path / 'backtest_results.xlsx') as writer:
                records_df.to_excel(writer, sheet_name='Trade Records', index=False)
                stats_df.to_excel(writer, sheet_name='Summary', index=False)

            logger.info(f"结果已导出到: {output_path / 'backtest_results.xlsx'}")

        except Exception as e:
            logger.error(f"导出结果时发生错误: {str(e)}")
            raise

    @staticmethod
    def generate_report(results: BacktestResults, records: List[TradeRecord]) -> dict:
        """
        生成详细的回测报告

        Args:
            results: 回测结果对象
            records: 交易记录列表

        Returns:
            dict: 包含各种统计数据的字典
        """
        if not records:
            return {}

        df = pd.DataFrame([record.to_dict() for record in records])

        # 计算额外的统计数据
        profitable_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]

        report = {
            'summary': {
                'initial_value': results.initial_value,
                'final_value': results.final_value,
                'total_return': results.total_return,
                'annual_return': results.annual_return,
                'sharpe_ratio': results.sharpe_ratio,
                'max_drawdown': results.max_drawdown,
                'max_drawdown_amount': results.max_drawdown_amount,
            },
            'trade_stats': {
                'total_trades': len(records),
                'winning_trades': len(profitable_trades),
                'losing_trades': len(losing_trades),
                'win_rate': results.win_rate,
                'avg_win': profitable_trades['pnl'].mean() if not profitable_trades.empty else 0,
                'avg_loss': losing_trades['pnl'].mean() if not losing_trades.empty else 0,
                'largest_win': profitable_trades['pnl'].max() if not profitable_trades.empty else 0,
                'largest_loss': losing_trades['pnl'].min() if not losing_trades.empty else 0,
                'avg_trade_duration': calculate_avg_trade_duration(df),
            },
            'monthly_returns': calculate_monthly_returns(df),
        }

        return report


def calculate_avg_trade_duration(df: pd.DataFrame) -> str:
    """计算平均交易持续时间"""
    if df.empty or len(df) < 2:
        return "N/A"

    df['datetime'] = pd.to_datetime(df['datetime'])
    buy_times = df[df['action'] == 'BUY']['datetime']
    sell_times = df[df['action'] == 'SELL']['datetime']

    if len(buy_times) != len(sell_times):
        return "N/A"

    durations = sell_times.values - buy_times.values
    avg_duration = durations.mean()

    return str(avg_duration)


def calculate_monthly_returns(df: pd.DataFrame) -> pd.Series:
    """计算月度收益率"""
    if df.empty:
        return pd.Series()

    df['datetime'] = pd.to_datetime(df['datetime'])
    monthly_pnl = df.set_index('datetime')['pnl'].resample('M').sum()
    return monthly_pnl
