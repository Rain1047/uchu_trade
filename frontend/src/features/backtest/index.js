import React from 'react';
import { Container, Paper, Typography, Box, CircularProgress } from '@material-ui/core';
import { useStyles } from './utils/styles';
import { useBacktest } from './hooks/useBacktest';
import { BacktestControls } from './components/BacktestControls';
import { BacktestStatistics } from './components/BacktestStatistics';
import { BacktestRecords } from './components/BacktestRecords';
import {BacktestChart} from "./components/BacktestChart";

const BacktestResults = () => {
  const classes = useStyles();
  const {
    symbols,
    selectedSymbol,
    setSelectedSymbol,
    strategies,
    selectedStrategy,
    setSelectedStrategy,
    backtestKeys,
    selectedKey,
    setSelectedKey,
    records,
    details,
    loading,
    error
  } = useBacktest();

  if (error) {
    return (
      <Container className={classes.root}>
        <Paper className={classes.paper}>
          <Typography color="error">{error}</Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container className={classes.root}>
      <Paper className={classes.paper}>
        <Typography variant="h5" gutterBottom>回测结果分析</Typography>

        <BacktestControls
          symbols={symbols}
          selectedSymbol={selectedSymbol}
          onSymbolChange={setSelectedSymbol}
          strategies={strategies}
          selectedStrategy={selectedStrategy}
          onStrategyChange={setSelectedStrategy}
          backtestKeys={backtestKeys}
          selectedKey={selectedKey}
          onKeyChange={setSelectedKey}
        />

        {loading ? (
          <Box className={classes.loading}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <BacktestStatistics details={details} />
            {/*<BacktestRecords records={records} />*/}
            {loading ? (
            <Box className={classes.loading}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <BacktestStatistics details={details} />
              <BacktestChart records={records} />
            </>
)}
          </>
        )}
      </Paper>
    </Container>
  );
};

export default BacktestResults;