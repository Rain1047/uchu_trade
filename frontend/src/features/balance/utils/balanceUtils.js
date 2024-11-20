export const calculatePrice = (eq_usd, avail_bal) => {
    if (!avail_bal || parseFloat(avail_bal) === 0) return '0';
    return (parseFloat(eq_usd) / parseFloat(avail_bal)).toFixed(2);
};

export const formatBalance = (balance) => {
    if (!balance) return '0';
    return parseFloat(balance).toFixed(4);
};


export const formatNumber = (value, precision = 4) => {
    if (!value) return '0';
    const num = parseFloat(value);
    return num.toLocaleString(undefined, {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision
    });
};

export const formatPrice = (value) => {
    if (!value) return '0';
    return parseFloat(value).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
};

export const formatPnL = (value) => {
    if (!value) return '+0';
    const num = parseFloat(value);
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
};

export const calculatePnLPercentage = (pnl, position) => {
    if (!pnl || !position) return '+0.00%';
    const percentage = (pnl / position) * 100;
    const sign = percentage >= 0 ? '+' : '';
    return `${sign}${percentage.toFixed(2)}%`;
};