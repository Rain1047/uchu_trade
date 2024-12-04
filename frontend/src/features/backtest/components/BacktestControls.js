import React from 'react';
import {Box, FormControl, InputLabel, Select, MenuItem, Button} from '@material-ui/core';
import { useStyles } from '../utils/styles';
import { PlayArrow as PlayArrowIcon } from '@material-ui/icons';

export const BacktestControls = ({
  symbols,
  selectedSymbol,
  onSymbolChange,
  strategies,
  selectedStrategy,
  onStrategyChange,
  backtestKeys,
  selectedKey,
  onKeyChange,
  onRunBacktest,
  runningBacktest
}) => {
  const classes = useStyles();

  return (
    <Box className={classes.controls}>
      <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel>交易对</InputLabel>
        <Select
          value={selectedSymbol}
          onChange={(e) => onSymbolChange(e.target.value)}
          label="交易对"
        >
          {symbols.map((symbol) => (
            <MenuItem key={symbol} value={symbol}>{symbol}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel>策略</InputLabel>
        <Select
          value={selectedStrategy}
          onChange={(e) => onStrategyChange(e.target.value)}
          label="策略"
        >
          {strategies.map((strategy) => (
            <MenuItem key={strategy.id} value={strategy.id}>
              {strategy.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Button
        variant="contained"
        color="primary"
        onClick={onRunBacktest}
        disabled={runningBacktest || !selectedStrategy}
        startIcon={<PlayArrowIcon />}
        className={classes.runButton}
      >
        {runningBacktest ? '运行中...' : '运行回测'}
      </Button>

      <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel>回测记录</InputLabel>
        <Select
          value={selectedKey}
          onChange={(e) => onKeyChange(e.target.value)}
          label="回测记录"
        >
          {backtestKeys.map((key) => (
            <MenuItem key={key} value={key}>{key}</MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};