import React, { useState, useEffect, useCallback } from 'react';
import { Box, Container, Typography, CircularProgress, Grid } from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import { BacktestControls } from './components/BacktestControls';
import { BacktestResults } from './components/BacktestResults';
import { BacktestChart } from './components/BacktestChart';
import { BacktestStatistics } from './components/BacktestStatistics';
import { useBacktestApi } from './hooks/useBacktestApi';
import { fetchBacktestData } from './utils/backtestAPI';

const BacktestPage = () => {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [runningBacktest, setRunningBacktest] = useState(false);
  const [backtestData, setBacktestData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { listStrategies, runBacktest } = useBacktestApi();

  // 获取策略列表
  useEffect(() => {
    const fetchStrategies = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await listStrategies();
        if (result.success) {
          setStrategies(result.data);
        } else {
          throw new Error(result.message || '获取策略列表失败');
        }
      } catch (error) {
        console.error('Failed to fetch strategies:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchStrategies();
  }, []);

  // 运行回测
  const handleRunBacktest = async () => {
    if (!selectedStrategy) return;
    
    setRunningBacktest(true);
    setError(null);
    try {
      const result = await runBacktest(selectedStrategy);
      if (result.success) {
        // 处理双层嵌套的data结构
        const actualData = result.data?.data || result.data;
        setBacktestData(actualData);
      } else {
        throw new Error(result.message || '运行回测失败');
      }
    } catch (error) {
      console.error('Failed to run backtest:', error);
      setError(error.message);
    } finally {
      setRunningBacktest(false);
    }
  };

  // 获取回测数据
  const fetchBacktestDetails = useCallback(async (key) => {
    if (!key) return;
    
    // 如果已经有相同key的数据，不再重复请求
    if (backtestData && backtestData.key === key) {
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      // 使用 Promise.all 并行获取数据
      const [recordsResult, detailsResult] = await Promise.all([
        fetchBacktestData.getRecords(key),
        fetchBacktestData.getDetails(key)
      ]);

      if (recordsResult.success && detailsResult.success) {
        setBacktestData({
          records: recordsResult.data,
          details: detailsResult.data,
          key: key
        });
      } else {
        throw new Error('获取回测记录失败');
      }
    } catch (error) {
      console.error('Failed to fetch backtest data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [backtestData]);

  // 处理回测记录变更
  const handleBacktestKeyChange = useCallback((key) => {
    fetchBacktestDetails(key);
  }, [fetchBacktestDetails]);

  // 当策略改变时，清空回测数据
  useEffect(() => {
    setBacktestData(null);
  }, [selectedStrategy]);

  if (loading) {
    return (
      <Container>
        <Box my={4} display="flex" justifyContent="center" alignItems="center">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box my={4}>
        <Typography variant="h4" gutterBottom>
          回测中心
        </Typography>
        
        {error && (
          <Box mb={2}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}

        <BacktestControls
          strategies={strategies}
          selectedStrategy={selectedStrategy}
          onStrategyChange={setSelectedStrategy}
          onRunBacktest={handleRunBacktest}
          runningBacktest={runningBacktest}
          onBacktestKeyChange={handleBacktestKeyChange}
        />

        {backtestData && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <BacktestResults results={backtestData.details?.results || backtestData.results} />
            </Grid>
            <Grid item xs={12}>
              <BacktestStatistics details={backtestData.details?.results || backtestData.results} />
            </Grid>
            <Grid item xs={12}>
              <BacktestChart 
                records={backtestData.records} 
                details={backtestData.details}
                strategyInfo={{
                  name: backtestData.details?.results?.strategy_name || backtestData.results?.strategy_name,
                  symbol: backtestData.details?.results?.symbol || backtestData.results?.symbol,
                  timeframe: backtestData.details?.results?.timeframe || backtestData.results?.timeframe,
                  parameters: backtestData.details?.results?.parameters || backtestData.results?.parameters
                }}
              />
            </Grid>
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default BacktestPage;