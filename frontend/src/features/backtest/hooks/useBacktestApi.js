import { API_ENDPOINTS, BASE_URL } from '../constants/backtest';

export const useBacktestApi = () => {
  const listStrategies = async () => {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_STRATEGIES}`);
    if (!response.ok) {
      throw new Error('获取策略列表失败');
    }
    return response.json();
  };

  const runBacktest = async (strategyId) => {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.RUN_BACKTEST}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ strategy_id: strategyId }),
    });

    if (!response.ok) {
      throw new Error('运行回测失败');
    }
    return response.json();
  };

  return {
    listStrategies,
    runBacktest,
  };
}; 