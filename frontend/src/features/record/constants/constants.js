// features/record/constants.js
export const TRADE_TYPES = [
  { label: '限价买入', value: 'limit_order' },
  { label: '市价买入', value: 'market_buy' },
  { label: '止损', value: 'stop_loss' },
  { label: '市价卖出', value: 'market_sell' }
];

export const TRADE_SIDES = [
  { label: '买入', value: 'buy' },
  { label: '卖出', value: 'sell' }
];

export const EXEC_SOURCES = [
  { label: '手动', value: 'manual' },
  { label: '自动', value: 'auto' }
];

export const TIME_RANGES = [
  { label: '近一月', value: 30 },
  { label: '近三月', value: 90 },
  { label: '近一年', value: 365 }
];