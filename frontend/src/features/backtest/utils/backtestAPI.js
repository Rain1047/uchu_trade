import { API_ENDPOINTS, BASE_URL } from '../constants/backtest';

export const fetchBacktestData = {
  async getSymbols() {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_SYMBOL}`);
    return response.json();
  },

  async getStrategies(symbol) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_STRATEGY}?symbol=${symbol}`);
    return response.json();
  },

  async getKeys(strategyId, symbol) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_KEY}?strategy_id=${strategyId}&symbol=${symbol}`);
    return response.json();
  },

  async getRecords(key) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.LIST_RECORD}?key=${key}`);
    return response.json();
  },

  async getDetails(key) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.GET_DETAIL}?key=${key}`);
    return response.json();
  }
};