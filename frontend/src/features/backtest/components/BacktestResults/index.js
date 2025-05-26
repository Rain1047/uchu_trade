import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  makeStyles
} from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(3),
  },
  paper: {
    padding: theme.spacing(3),
  },
  metric: {
    textAlign: 'center',
    padding: theme.spacing(2),
  },
  metricValue: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: theme.palette.primary.main,
  },
  metricLabel: {
    color: theme.palette.text.secondary,
  },
}));

export const BacktestResults = ({ results }) => {
  const classes = useStyles();

  // 添加默认值
  const defaultResults = {
    symbol: '',
    strategy_name: '',
    test_finished_time: '',
    buy_signal_count: 0,
    sell_signal_count: 0,
    transaction_count: 0,
    profit_count: 0,
    loss_count: 0,
    profit_total_count: 0,
    profit_average: 0,
    profit_rate: 0
  };

  // 合并默认值和实际结果
  const safeResults = { ...defaultResults, ...results };

  const metrics = [
    { label: '交易对', value: safeResults.symbol },
    { label: '策略名称', value: safeResults.strategy_name },
    { label: '运行时间', value: safeResults.test_finished_time },
    { label: '买入信号次数', value: safeResults.buy_signal_count },
    { label: '卖出信号次数', value: safeResults.sell_signal_count },
    { label: '总交易次数', value: safeResults.transaction_count },
    { label: '获利次数', value: safeResults.profit_count },
    { label: '损失次数', value: safeResults.loss_count },
    { label: '总收益', value: `$${safeResults.profit_total_count.toFixed(2)}` },
    { label: '平均收益', value: `$${safeResults.profit_average.toFixed(2)}` },
    { label: '收益率', value: `${safeResults.profit_rate.toFixed(2)}%` },
  ];

  return (
    <Box className={classes.root}>
      <Paper className={classes.paper}>
        <Typography variant="h6" gutterBottom>
          回测结果
        </Typography>
        <Grid container spacing={2}>
          {metrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Box className={classes.metric}>
                <Typography variant="h6" className={classes.metricValue}>
                  {metric.value}
                </Typography>
                <Typography variant="body2" className={classes.metricLabel}>
                  {metric.label}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
}; 