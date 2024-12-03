import React from 'react';
import { Box, Grid, Paper, Typography } from '@material-ui/core';
import { useStyles } from '../utils/styles';

export const BacktestRecords = ({ records }) => {
  const classes = useStyles();

  return (
    <Box mt={4}>
      <Typography variant="h6" gutterBottom>交易记录</Typography>
      <Grid container spacing={2}>
        {records.map((record) => (
          <Grid item xs={12} key={record.id}>
            <Paper className={classes.recordPaper}>
              <Typography>
                时间: {record.transaction_time}
              </Typography>
              <Typography>
                PnL: ${record.transaction_pnl}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {record.transaction_result}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};