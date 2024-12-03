import React from 'react';
import { Box, Typography } from '@material-ui/core';
import { useStyles } from '../utils/styles';

export const BacktestStatistics = ({ details }) => {
  const classes = useStyles();

  if (!details) return null;

  const stats = [
    { label: '总交易次数', value: details.transaction_count },
    { label: '盈利次数', value: details.profit_count },
    { label: '亏损次数', value: details.loss_count },
    { label: '胜率', value: `${details.profit_rate}%` },
    { label: '平均收益', value: details.profit_average },
    { label: '总收益', value: details.profit_total_count }
  ];

  return (
    <Box className={classes.statsContainer}>
      {stats.map((stat) => (
        <Box key={stat.label} className={classes.statItem}>
          <Typography variant="h6" color="primary">{stat.value}</Typography>
          <Typography color="textSecondary">{stat.label}</Typography>
        </Box>
      ))}
    </Box>
  );
};