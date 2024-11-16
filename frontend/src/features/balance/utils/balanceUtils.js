export const calculatePrice = (eq_usd, avail_bal) => {
    if (!avail_bal || parseFloat(avail_bal) === 0) return '0';
    return (parseFloat(eq_usd) / parseFloat(avail_bal)).toFixed(2);
};

export const formatNumber = (value, decimals = 2) => {
    if (!value) return '0';
    return parseFloat(value).toFixed(decimals);
};

export const formatBalance = (balance) => {
    if (!balance) return '0';
    return parseFloat(balance).toFixed(4);
};