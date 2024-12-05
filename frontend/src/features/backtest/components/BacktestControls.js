import React from 'react';
import {Box, FormControl, InputLabel, Select, MenuItem, Button, CircularProgress} from '@material-ui/core';
// import { useStyles } from '../utils/styles';
import { PlayArrow as PlayArrowIcon } from '@material-ui/icons';
import {makeStyles} from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
     controls: {
       display: 'flex',
       gap: theme.spacing(2),
       marginBottom: theme.spacing(3),
       alignItems: 'center',
       paddingRight: theme.spacing(4),
     },
     leftControls: {
       display: 'flex',
       gap: theme.spacing(2),
       flex: 1,
         paddingRight: theme.spacing(4),
     },
     formControl: {
       minWidth: 200,
     },
     runButton: {
       minWidth: 120,
       '& .MuiCircularProgress-root': {
         marginRight: theme.spacing(1),
         color: 'white'
       }
     }
    }));

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
        <Box className={classes.leftControls}>
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
              {runningBacktest && (
                <CircularProgress size={24} className={classes.buttonProgress} />
              )}
          </Button>
        </Box>

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