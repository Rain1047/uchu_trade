import { IconButton, Tooltip } from '@material-ui/core';
import { PlayArrow as PlayArrowIcon } from '@material-ui/icons';
import { fetchBacktestData } from '../utils/backtestAPI';

const RunBacktest = ({ strategyId, onSuccess }) => {
  const handleRun = async () => {
    try {
      const response = await fetchBacktestData.runBacktest(strategyId);
      if (response.success) {
        onSuccess?.();
      }
    } catch (error) {
      console.error('Failed to run backtest:', error);
    }
  };

  return (
    <Tooltip title="运行回测">
      <IconButton onClick={handleRun} color="primary">
        <PlayArrowIcon />
      </IconButton>
    </Tooltip>
  );
};

export default RunBacktest;