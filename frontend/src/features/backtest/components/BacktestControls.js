import React, { useEffect, useState, useCallback, useRef } from 'react';
import {Box, FormControl, InputLabel, Select, MenuItem, Button, CircularProgress} from '@material-ui/core';
// import { useStyles } from '../utils/styles';
import { PlayArrow as PlayArrowIcon } from '@material-ui/icons';
import {makeStyles} from "@material-ui/core/styles";
import { fetchBacktestData } from '../utils/backtestAPI';
import debounce from 'lodash/debounce';

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
  strategies,
  selectedStrategy,
  onStrategyChange,
  onRunBacktest,
  runningBacktest,
  onBacktestKeyChange
}) => {
  const classes = useStyles();
  const [backtestKeys, setBacktestKeys] = useState([]);
  const [selectedKey, setSelectedKey] = useState('');
  const [loading, setLoading] = useState(false);
  const isFirstRender = useRef(true);

  // 获取回测记录列表
  const fetchBacktestKeys = useCallback(async (strategyId, shouldAutoSelect = false) => {
    if (!strategyId) return;
    
    setLoading(true);
    try {
      const result = await fetchBacktestData.getKeys(strategyId);
      if (result.success) {
        setBacktestKeys(result.data);
        // 只在首次加载或明确要求时自动选择第一个
        if (result.data.length > 0 && (shouldAutoSelect || isFirstRender.current)) {
          setSelectedKey(result.data[0]);
          onBacktestKeyChange?.(result.data[0]);
          isFirstRender.current = false;
        }
      }
    } catch (error) {
      console.error('Failed to fetch backtest keys:', error);
    } finally {
      setLoading(false);
    }
  }, [onBacktestKeyChange]);

  // 当策略改变时，获取对应的回测记录
  useEffect(() => {
    // 策略改变时，清空当前选中的记录
    setSelectedKey('');
    fetchBacktestKeys(selectedStrategy, true);
  }, [selectedStrategy, fetchBacktestKeys]);

  const handleKeyChange = (event) => {
    const newKey = event.target.value;
    setSelectedKey(newKey);
    onBacktestKeyChange?.(newKey);
  };

  return (
    <Box className={classes.controls}>
        <Box className={classes.leftControls}>
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

          <FormControl variant="outlined" className={classes.formControl}>
            <InputLabel>回测记录</InputLabel>
            <Select
              value={selectedKey}
              onChange={handleKeyChange}
              label="回测记录"
              disabled={loading}
            >
              {backtestKeys.map((key) => (
                <MenuItem key={key} value={key}>
                  {key}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            color="primary"
            onClick={onRunBacktest}
            disabled={runningBacktest || !selectedStrategy || loading}
            startIcon={<PlayArrowIcon />}
            className={classes.runButton}
          >
            {runningBacktest ? '运行中...' : '运行回测'}
              {runningBacktest && (
                <CircularProgress size={24} className={classes.buttonProgress} />
              )}
          </Button>
        </Box>
    </Box>
  );
};