export const validationRules = {
  name: (value) => {
    if (!value) return '策略名称不能为空';
    if (value.length < 2) return '策略名称至少2个字符';
    return '';
  },
  trade_pair: (value) => !value ? '请选择交易对' : '',
  time_frame: (value) => !value ? '请选择时间窗' : '',
  // ... 其他验证规则
};
