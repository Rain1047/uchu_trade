// features/record/types.js
export const TradeRecord = {
  id: Number,
  ccy: String,
  type: String,
  amount: String,
  exec_price: String,
  exec_source: String,
  side: String,
  uTime: String,
  note: String
};

export const TradeRecordQuery = {
  pageNum: Number,
  pageSize: Number,
  ccy: String,
  type: Array,
  side: String,
  exec_source: String,
  beginTime: String,
  endTime: String
};