import { API_ENDPOINTS } from '../constants/historyConstants';

export const fetchTradeHistory = async (filters) => {
  const response = await fetch(API_ENDPOINTS.LIST_HISTORY, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters)
  });
  return response.json();
};