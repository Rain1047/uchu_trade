import { API_ENDPOINTS, BASE_URL } from '../constants/backtest';

export const fetchBacktestData = {
  async getSymbols() {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_SYMBOL}`);
    return response.json();
  },

  async getStrategies() {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_STRATEGIES}`);
    return response.json();
  },

  async getKeys(strategyId) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_KEY}?strategy_id=${strategyId}`);
    return response.json();
  },

  async getRecords(key) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_RECORD}?key=${key}`);
    return response.json();
  },

  async getDetails(key) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.GET_DETAIL}?key=${key}`);
    return response.json();
  },

  async getBacktestResults(params) {
    const queryParams = new URLSearchParams(params).toString();
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_BACKTEST_RESULTS}?${queryParams}`);
    return response.json();
  },

  async runBacktest(strategyId) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.RUN_BACKTEST}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy_id: strategyId })
    });
    return response.json();
  }
};