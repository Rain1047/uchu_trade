export const formatTimestamp = (timestamp) => {
  try {
    const date = new Date(parseInt(timestamp));
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (error) {
    return timestamp;
  }
};

export const calculateAmount = (price, size, fee) => {
  return ((parseFloat(price) * parseFloat(size)) + parseFloat(fee)).toFixed(2);
};