export const TRADE_INDICATORS = [
    { value: 'SMA', label: 'SMA' },
    { value: 'EMA', label: 'EMA' },
];

export const TABLE_COLUMNS = [
    { id: 'ccy', label: '币种' },
    { id: 'avail_bal', label: '可交易数量', align: 'right' },
    { id: 'eq_usd', label: '美金价值($)', align: 'right' },
    { id: 'current_price', label: '当前价格($)', align: 'right' },
    { id: 'acc_avg_px', label: '持仓均价($)', align: 'right' },
    { id: 'stop_loss_switch', label: '自动止损', align: 'center' },
    { id: 'limit_order_switch', label: '自动限价', align: 'center' },
];

export const API_ENDPOINTS = {
    BALANCE: 'http://127.0.0.1:8000/api/balance',
    BALANCE_RESET: 'http://127.0.0.1:8000/api/balance/reset',
    AUTO_CONFIG: 'http://127.0.0.1:8000/api/balance/auto_config'
};