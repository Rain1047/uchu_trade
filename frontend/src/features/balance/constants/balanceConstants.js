// export const TABLE_COLUMNS = [
//     { id: 'ccy', label: '币种', align: 'left' },
//     { id: 'avail_bal', label: '可交易数量', align: 'right' },
//     { id: 'eq_usd', label: '美金价值($)', align: 'right' },
//     { id: 'current_price', label: '当前价格($)', align: 'right' },
//     { id: 'acc_avg_px', label: '持仓均价($)', align: 'right' },
//     // { id: 'stop_loss_switch', label: '自动止损', align: 'center' },
//     // { id: 'limit_order_switch', label: '自动限价', align: 'center' }
// ];

// API 端点配置
export const API_ENDPOINTS = {
  LIST_BALANCE: 'http://127.0.0.1:8000/api/balance/list_balance',
  AUTO_CONFIG: 'http://127.0.0.1:8000/api/balance/auto_config',
  TOGGLE_SWITCH: 'http://127.0.0.1:8000/api/balance/toggle_switch',
  LIST_POSITIONS: 'http://127.0.0.1:8000/api/balance/list_positions',
  LIST_ORDERS: 'http://127.0.0.1:8000/api/balance/list_orders'
};



// constants/balanceConstants.js
export const TABLE_COLUMNS = [
  { id: 'ccy', label: '币种', align: 'left' },
  { id: 'availBal', label: '可用余额', align: 'right' },
  { id: 'eqUsd', label: '美元价值', align: 'right' },
];

// Mock data
export const mockPositions = {
  'BTC': [
    { size: '0.5', avgPrice: '42000', pnl: '+2.5%', margin: '1000' },
    { size: '0.3', avgPrice: '41500', pnl: '-1.2%', margin: '800' }
  ],
  'ETH': [
    { size: '5.0', avgPrice: '2200', pnl: '+3.1%', margin: '500' }
  ]
};

export const mockOrders = {
  'BTC': [
    { price: '43000', size: '0.2', type: 'limit', side: 'buy' },
    { price: '41000', size: '0.3', type: 'stop', side: 'sell' }
  ],
  'ETH': [
    { price: '2300', size: '2.0', type: 'limit', side: 'sell' }
  ]
};

// API 响应状态码
export const API_STATUS = {
  SUCCESS: 0,
  ERROR: 1,
  UNAUTHORIZED: 401
};

// 配置类型
export const CONFIG_TYPES = {
  STOP_LOSS: 'stop_loss',
  LIMIT_ORDER: 'limit_order'
};

export const ORDER_STATUS = {
    ACTIVE: 'active',
    FILLED: 'filled',
    CANCELED: 'canceled',
    REJECTED: 'rejected'
};

export const TRADE_INDICATORS = [
    { value: 'SMA', label: 'SMA' },
    { value: 'EMA', label: 'EMA' },
    { value: 'MACD', label: 'MACD' },
    { value: 'RSI', label: 'RSI' },
    { value: 'BOLL', label: 'BOLL' }
];

export const POSITION_SIDES = {
    LONG: 'long',
    SHORT: 'short'
};

export const ORDER_TYPES = {
    LIMIT: 'limit',
    MARKET: 'market',
    STOP: 'stop',
    STOP_LIMIT: 'stop_limit'
};

export const ORDER_SIDES = {
    BUY: 'buy',
    SELL: 'sell'
};

export const TIME_INTERVALS = [
    { value: '1m', label: '1分钟' },
    { value: '5m', label: '5分钟' },
    { value: '15m', label: '15分钟' },
    { value: '1h', label: '1小时' },
    { value: '4h', label: '4小时' },
    { value: '1d', label: '1天' }
];