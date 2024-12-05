export const API_ENDPOINTS = {
  LIST_HISTORY: 'http://127.0.0.1:8000/api/trade/list_history'
};

export const INITIAL_FILTERS = {
  pageSize: 10,
  pageNum: 1,
  inst_id: '',
  fill_start_time: '',
  fill_end_time: ''
};

export const MOCK_DATA = {
  items: [{
    trade_id: 'MOCK-001',
    inst_id: 'BTC-USDT',
    side: 'buy',
    fill_px: '42000.50',
    fill_sz: '0.1234',
    fee: '-0.000123',
    fill_time: '1699000000000',
    note: ''
  }],
  total_count: 3,
  page_size: 10,
  page_num: 1
};