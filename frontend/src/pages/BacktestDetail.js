import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  ToggleButton,
  ToggleButtonGroup,
  Pagination,
  Button,
  FormControl,
  Select,
  MenuItem,
  Divider,
  Chip,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  ArrowBack,
  TrendingUp,
  TrendingDown,
  ShowChart,
  SwapHoriz,
  ArrowUpward,
  ArrowDownward,
  AccountBalance,
  AccessTime,
  Assessment,
  Close,
  Delete,
  Info,
  Visibility,
  Refresh
} from '@mui/icons-material';
import http from '../api/http';
import { useNavigate, useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend as RechartsLegend, ResponsiveContainer, BarChart, Bar, ComposedChart, Area, Cell } from 'recharts';
import { useTheme } from '@mui/material/styles';
import { format } from 'date-fns';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend
} from 'chart.js';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  ChartLegend
);

// API基础URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const BacktestDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backtestData, setBacktestData] = useState(null);
  const [sortBy, setSortBy] = useState('win_rate');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [selectedSymbol, setSelectedSymbol] = useState('ALL');
  const [transactionData, setTransactionData] = useState(null);
  const [transactionLoading, setTransactionLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('info');
  const [symbolDetailOpen, setSymbolDetailOpen] = useState(false);
  const [selectedSymbolDetail, setSelectedSymbolDetail] = useState(null);
  const [symbolTransactions, setSymbolTransactions] = useState(null);

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  const loadBacktestDetail = async () => {
    setLoading(true);
    try {
      const response = await http.get(`/api/enhanced-backtest/record/${id}`);
      if (response.data.success) {
        setBacktestData(response.data.data);
      } else {
        setError(response.data.error);
        setSnackbarOpen(true);
      }
    } catch (err) {
      setError('加载回测详情失败');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const loadTransactionDetail = async (symbol) => {
    setTransactionLoading(true);
    try {
      const response = await http.get(`/api/enhanced-backtest/record/${id}/symbol/${symbol}/transactions`);
      if (response.data.success) {
        setTransactionData(response.data);
      } else {
        setError(response.data.error);
        setSnackbarOpen(true);
      }
    } catch (err) {
      setError('加载交易记录失败');
      setSnackbarOpen(true);
    } finally {
      setTransactionLoading(false);
    }
  };

  useEffect(() => {
    loadBacktestDetail();
  }, [id]);

  useEffect(() => {
    const checkBacktestStatus = async () => {
      try {
        const res = await http.get(`/api/enhanced-backtest/record/${id}`);
        const data = res.data.success ? res.data.data : null;
        
        if (data && data.status === 'running' && !loading) {
          showSnackbar(`回测已开始执行，记录ID: ${id}`, 'info');
        }
        
        if (data) setBacktestData(data);
        setLoading(false);
      } catch (error) {
        console.error('获取回测详情失败:', error);
        setError('获取回测详情失败');
        setLoading(false);
      }
    };

    if (id) {
      checkBacktestStatus();
      const interval = setInterval(checkBacktestStatus, 30000); // 30秒
      return () => clearInterval(interval);
    }
  }, [id]);

  const getSortedData = () => {
    const list = backtestData?.symbol_results || backtestData?.result?.individual_results || [];
    if (!Array.isArray(list)) return [];
    
    const sorted = [...list].sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortOrder === 'desc') {
        return bValue - aValue;
      } else {
        return aValue - bValue;
      }
    });
    
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return sorted.slice(startIndex, endIndex);
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setPage(1);
  };

  const getSummaryData = () => {
    const results = backtestData?.symbol_results || backtestData?.result?.individual_results || [];
    if (!Array.isArray(results) || results.length === 0) return null;
    
    const totalSymbols = results.length;
    const profitableSymbols = results.filter(r => r.total_profit > 0).length;
    const losingSymbols = totalSymbols - profitableSymbols;
    
    const totalTrades = results.reduce((sum, r) => sum + r.total_trades, 0);
    const totalWinningTrades = results.reduce((sum, r) => sum + r.winning_trades, 0);
    const avgWinRate = totalTrades > 0 ? (totalWinningTrades / totalTrades * 100) : 0;
    
    return {
      totalSymbols,
      profitableSymbols,
      losingSymbols,
      avgWinRate
    };
  };

  const handleSymbolChange = async (sym) => {
    setSelectedSymbol(sym);
    setTransactionData(null);
    if (sym === 'ALL') return;
    await loadTransactionDetail(sym);
  };

  const prepareChartData = () => {
    if (!transactionData || !transactionData.records) return [];
    
    let cumulativePnL = 0;
    return transactionData.records.map((record, index) => {
      cumulativePnL += record.transaction_pnl;
      return {
        name: `交易${index + 1}`,
        date: record.transaction_time,
        pnl: record.transaction_pnl,
        cumulative: cumulativePnL,
        profit: record.transaction_pnl > 0 ? record.transaction_pnl : 0,
        loss: record.transaction_pnl < 0 ? Math.abs(record.transaction_pnl) : 0
      };
    });
  };

  const summary = getSummaryData();
  const sortedData = getSortedData();
  const listAll = backtestData?.symbol_results || backtestData?.result?.individual_results || [];
  const totalPages = listAll && Array.isArray(listAll) ? Math.ceil(listAll.length / pageSize) : 0;
  const symbolOptions = listAll.map(r => r.symbol) || [];
  const chartData = prepareChartData();

  const { status, progress, result, message } = backtestData || {};

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress sx={{ color: '#5eddac' }} />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/enhanced-backtest')}
            sx={{ mt: 2 }}
          >
            返回回测列表
          </Button>
        </Paper>
      </Container>
    );
  }

  const renderStatus = () => {
    let statusColor;
    let statusIcon;
    
    switch (status) {
      case 'running':
        statusColor = 'primary';
        statusIcon = <CircularProgress size={20} />;
        break;
      case 'completed':
        statusColor = 'success';
        statusIcon = <TrendingUp />;
        break;
      case 'failed':
        statusColor = 'error';
        statusIcon = <TrendingDown />;
        break;
      case 'cancelled':
        statusColor = 'warning';
        statusIcon = <Close />;
        break;
      default:
        statusColor = 'default';
        statusIcon = <Info />;
    }
    
    return (
      <Box display="flex" alignItems="center" gap={1}>
        {statusIcon}
        <Typography color={`${statusColor}.main`}>
          {message || status}
        </Typography>
        {status === 'running' && (
          <Typography variant="body2" color="text.secondary">
            ({progress}%)
          </Typography>
        )}
      </Box>
    );
  };

  const renderResults = () => {
    // 如果没有 result 对象但有 symbol_results，直接渲染详情表格
    if (!result && backtestData?.symbol_results) {
      const results = backtestData.symbol_results;
      
      return (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ 
              p: 2, 
              backgroundColor: '#23272a', 
              border: '1px solid #5eddac20',
              '& .MuiTypography-root': { color: '#fff' }
            }}>
              <Typography variant="h6" gutterBottom>
                回测配置
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    入场策略: {backtestData.entry_strategy}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    出场策略: {backtestData.exit_strategy}
                  </Typography>
                  {backtestData.filter_strategy && (
                    <Typography variant="body2" color="text.secondary">
                      过滤策略: {backtestData.filter_strategy}
                    </Typography>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    交易对: {backtestData.symbols.join(', ')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    时间框架: {backtestData.timeframe}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    初始资金: ${backtestData.initial_cash.toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
          
          <Grid item xs={12}>
            <Paper sx={{ 
              p: 2, 
              backgroundColor: '#23272a', 
              border: '1px solid #5eddac20',
              '& .MuiTypography-root': { color: '#fff' }
            }}>
              <Typography variant="h6" gutterBottom>
                交易对详情
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>交易对</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>总交易</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>胜/负</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>胜率</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>总盈亏</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>收益率</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>盈亏比</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>最大回撤</TableCell>
                      <TableCell align="center" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>操作</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.map((item) => (
                      <TableRow
                        key={item.symbol}
                        hover
                        sx={{
                          '&:hover': {
                            backgroundColor: '#5eddac10',
                          }
                        }}
                      >
                        <TableCell sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>{item.symbol}</TableCell>
                        <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>{item.total_trades}</TableCell>
                        <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>{item.winning_trades}/{item.losing_trades}</TableCell>
                        <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>{item.win_rate.toFixed(1)}%</TableCell>
                        <TableCell align="right" sx={{ color: item.total_profit >= 0 ? '#5eddac' : '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                          ${item.total_profit.toFixed(2)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: item.total_return >= 0 ? '#5eddac' : '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                          {(item.total_return * 100).toFixed(2)}%
                        </TableCell>
                        <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>
                          {item.profit_loss_ratio ? item.profit_loss_ratio.toFixed(2) : '-'}
                        </TableCell>
                        <TableCell align="right" sx={{ color: '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                          {(item.max_drawdown * 100).toFixed(2)}%
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            onClick={() => handleViewSymbolDetail(item.symbol)}
                            sx={{ color: '#5eddac' }}
                          >
                            <Visibility />
                          </IconButton>
                          <IconButton
                            size="small"
                            disabled
                            sx={{ color: '#999' }}
                            title="功能开发中"
                          >
                            <Assessment />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      );
    }
    
    // 如果没有 result 也没有 symbol_results，返回空
    if (!result) return null;
    
    const { config, total_symbols, avg_return, best_symbol, worst_symbol, total_trades_all, avg_win_rate } = result;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#23272a', 
            border: '1px solid #5eddac20',
            '& .MuiTypography-root': { color: '#fff' }
          }}>
            <Typography variant="h6" gutterBottom>
              回测配置
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  入场策略: {config.entry_strategy}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  出场策略: {config.exit_strategy}
                </Typography>
                {config.filter_strategy && (
                  <Typography variant="body2" color="text.secondary">
                    过滤策略: {config.filter_strategy}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  交易对: {config.symbols.join(', ')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  时间框架: {config.timeframe}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  初始资金: ${config.initial_cash.toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#23272a', 
            border: '1px solid #5eddac20',
            '& .MuiTypography-root': { color: '#fff' }
          }}>
            <Typography variant="h6" gutterBottom>
              汇总指标
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  交易对数量
                </Typography>
                <Typography variant="h6">
                  {total_symbols}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  平均收益率
                </Typography>
                <Typography variant="h6" color={avg_return >= 0 ? 'success.main' : 'error.main'}>
                  {(avg_return * 100).toFixed(2)}%
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  总交易次数
                </Typography>
                <Typography variant="h6">
                  {total_trades_all}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  平均胜率
                </Typography>
                <Typography variant="h6">
                  {avg_win_rate.toFixed(1)}%
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#23272a', 
            border: '1px solid #5eddac20',
            '& .MuiTypography-root': { color: '#fff' }
          }}>
            <Typography variant="h6" gutterBottom>
              最佳/最差表现
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  最佳交易对
                </Typography>
                <Typography variant="h6" color="success.main">
                  {best_symbol} ({result.best_return.toFixed(2)}%)
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  最差交易对
                </Typography>
                <Typography variant="h6" color="error.main">
                  {worst_symbol} ({result.worst_return.toFixed(2)}%)
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#23272a', 
            border: '1px solid #5eddac20',
            '& .MuiTypography-root': { color: '#fff' }
          }}>
            <Typography variant="h6" gutterBottom>
              交易对详情
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>交易对</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>收益率</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>年化收益</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>夏普比率</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>最大回撤</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>交易次数</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>胜率</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>总盈亏</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>收益率</TableCell>
                    <TableCell align="right" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>盈亏比</TableCell>
                    <TableCell align="center" sx={{ color: '#5eddac', borderBottom: '1px solid #5eddac20' }}>操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(result.individual_results || []).map((item) => (
                    <TableRow
                      key={item.symbol}
                      hover
                      sx={{
                        '&:hover': {
                          backgroundColor: '#5eddac10',
                        }
                      }}
                    >
                      <TableCell sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>{item.symbol}</TableCell>
                      <TableCell align="right" sx={{ color: item.total_return >= 0 ? '#5eddac' : '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                        {(item.total_return * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell align="right" sx={{ color: item.annual_return >= 0 ? '#5eddac' : '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                        {(item.annual_return * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>
                        {item.sharpe_ratio.toFixed(2)}
                      </TableCell>
                      <TableCell align="right" sx={{ color: '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                        {(item.max_drawdown * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>
                        {item.total_trades}
                      </TableCell>
                      <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>
                        {item.win_rate.toFixed(1)}%
                      </TableCell>
                      <TableCell align="right" sx={{ color: item.total_profit >= 0 ? '#5eddac' : '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                        ${item.total_profit.toFixed(2)}
                      </TableCell>
                      <TableCell align="right" sx={{ color: item.total_return >= 0 ? '#5eddac' : '#ff6b6b', borderBottom: '1px solid #5eddac10' }}>
                        {(item.total_return * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell align="right" sx={{ color: '#fff', borderBottom: '1px solid #5eddac10' }}>
                        {item.profit_loss_ratio ? item.profit_loss_ratio.toFixed(2) : '-'}
                      </TableCell>
                      <TableCell align="center" sx={{ borderBottom: '1px solid #5eddac10' }}>
                        <IconButton
                          size="small"
                          onClick={() => handleViewSymbolDetail(item.symbol)}
                          sx={{ color: '#5eddac' }}
                        >
                          <Visibility />
                        </IconButton>
                        <IconButton
                          size="small"
                          disabled
                          sx={{ color: '#999' }}
                          title="功能开发中"
                        >
                          <Assessment />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    );
  };

  const handleCancelBacktest = async () => {
    try {
      await axios.delete(`/api/enhanced-backtest/record/${id}`);
      showSnackbar('回测已取消', 'info');
      const response = await axios.get(`/api/enhanced-backtest/record/${id}`);
      setBacktestData(response.data);
    } catch (err) {
      showSnackbar('取消回测失败', 'error');
    }
  };

  const handleDeleteBacktest = async () => {
    try {
      await axios.delete(`/api/enhanced-backtest/record/${id}`);
      showSnackbar('回测已删除', 'info');
      navigate('/enhanced-backtest');
    } catch (err) {
      showSnackbar('删除回测失败', 'error');
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleViewSymbolDetail = async (symbol) => {
    try {
      setSymbolDetailOpen(true);
      setSelectedSymbolDetail(symbol);
      const response = await http.get(`/api/enhanced-backtest/record/${id}/symbol/${symbol}/transactions`);
      if (response.data.success) {
        setSymbolTransactions(response.data);
      }
    } catch (error) {
      showSnackbar('加载交易详情失败', 'error');
    }
  };

  const handleCloseSymbolDetail = () => {
    setSymbolDetailOpen(false);
    setSelectedSymbolDetail(null);
    setSymbolTransactions(null);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4, backgroundColor: '#181c1f', minHeight: '100vh' }}>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center' }}>
        <IconButton onClick={() => navigate('/enhanced-backtest')} sx={{ mr: 2, color: '#5eddac' }}>
          <ArrowBack />
        </IconButton>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center' }}>
            回测详情 #{id}
          </Typography>
          {backtestData && (
            <Typography variant="body2" sx={{ color: '#ccc', mt: 1 }}>
              {backtestData.entry_strategy || backtestData?.result?.config?.entry_strategy}/
              {backtestData.exit_strategy || backtestData?.result?.config?.exit_strategy}
              { (backtestData.filter_strategy || backtestData?.result?.config?.filter_strategy) && `/${backtestData.filter_strategy || backtestData?.result?.config?.filter_strategy}` }
              {' - '}
              {backtestData.timeframe || backtestData?.result?.config?.timeframe}
            </Typography>
          )}
        </Box>
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <Button
            variant="outlined"
            startIcon={<ShowChart />}
            onClick={() => navigate('/enhanced-backtest')}
            sx={{ 
              mr: 1,
              color: '#5eddac',
              borderColor: '#5eddac',
              '&:hover': {
                borderColor: '#5eddac',
                backgroundColor: 'rgba(94, 237, 172, 0.1)'
              }
            }}
          >
            返回列表
          </Button>
          <IconButton 
            onClick={() => loadBacktestDetail()} 
            sx={{ color: '#5eddac' }}
            title="刷新数据"
          >
            <Refresh />
          </IconButton>
          {renderStatus()}
        </Box>
        <Box display="flex" gap={1}>
          {status === 'running' && (
            <Button
              variant="outlined"
              color="warning"
              startIcon={<Close />}
              onClick={handleCancelBacktest}
            >
              取消回测
            </Button>
          )}
          {status !== 'running' && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDeleteBacktest}
            >
              删除回测
            </Button>
          )}
        </Box>
      </Box>

      {renderResults()}

      {/* 交易详情对话框 */}
      <Dialog 
        open={symbolDetailOpen} 
        onClose={handleCloseSymbolDetail}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#23272a',
            color: '#fff',
            border: '1px solid #5eddac40'
          }
        }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid #5eddac20' }}>
          {selectedSymbolDetail} 交易详情
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {symbolTransactions && (
            <>
              {/* 总览信息 */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Box sx={{ p: 2, backgroundColor: '#0a0a0a', borderRadius: 1, border: '1px solid #5eddac20' }}>
                    <Typography variant="body2" sx={{ color: '#999' }}>总交易次数</Typography>
                    <Typography variant="h6" sx={{ color: '#5eddac' }}>
                      {symbolTransactions.results.transaction_count}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ p: 2, backgroundColor: '#0a0a0a', borderRadius: 1, border: '1px solid #5eddac20' }}>
                    <Typography variant="body2" sx={{ color: '#999' }}>盈利/亏损</Typography>
                    <Typography variant="h6">
                      <span style={{ color: '#5eddac' }}>{symbolTransactions.results.profit_count}</span>
                      <span style={{ color: '#fff' }}> / </span>
                      <span style={{ color: '#ff6b6b' }}>{symbolTransactions.results.loss_count}</span>
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ p: 2, backgroundColor: '#0a0a0a', borderRadius: 1, border: '1px solid #5eddac20' }}>
                    <Typography variant="body2" sx={{ color: '#999' }}>胜率</Typography>
                    <Typography variant="h6" sx={{ color: symbolTransactions.results.profit_rate >= 50 ? '#5eddac' : '#ff6b6b' }}>
                      {symbolTransactions.results.profit_rate}%
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ p: 2, backgroundColor: '#0a0a0a', borderRadius: 1, border: '1px solid #5eddac20' }}>
                    <Typography variant="body2" sx={{ color: '#999' }}>总盈亏</Typography>
                    <Typography variant="h6" sx={{ color: symbolTransactions.results.profit_total_count >= 0 ? '#5eddac' : '#ff6b6b' }}>
                      ${symbolTransactions.results.profit_total_count}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {/* 图表 */}
              {symbolTransactions.records && symbolTransactions.records.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>盈亏曲线</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart data={symbolTransactions.records.map((r, idx) => {
                      const cumulative = symbolTransactions.records.slice(0, idx + 1).reduce((sum, rec) => sum + rec.transaction_pnl, 0);
                      return {
                        ...r,
                        cumulative,
                        name: `交易${idx + 1}`
                      };
                    })}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="name" stroke="#999" />
                      <YAxis stroke="#999" />
                      <RechartsTooltip 
                        contentStyle={{ backgroundColor: '#23272a', border: '1px solid #5eddac40' }}
                        labelStyle={{ color: '#5eddac' }}
                        formatter={(value, name, props) => {
                          if (name === '单笔盈亏') {
                            return [`$${value}`, name];
                          }
                          if (name === '累计盈亏') {
                            return [`$${value.toFixed(2)}`, name];
                          }
                          return [value, name];
                        }}
                        labelFormatter={(label, payload) => {
                          if (payload && payload.length > 0) {
                            const data = payload[0].payload;
                            return `${label} (${data.transaction_time})`;
                          }
                          return label;
                        }}
                      />
                      <RechartsLegend />
                      <Bar dataKey="transaction_pnl" name="单笔盈亏">
                        {symbolTransactions.records.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.transaction_pnl >= 0 ? '#5eddac' : '#ff6b6b'} />
                        ))}
                      </Bar>
                      <Line type="monotone" dataKey="cumulative" stroke="#ffd93d" strokeWidth={2} name="累计盈亏" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </Box>
              )}

              {/* 交易记录表格 */}
              <TableContainer component={Paper} sx={{ backgroundColor: '#0a0a0a', border: '1px solid #5eddac20' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#5eddac' }}>交易时间</TableCell>
                      <TableCell sx={{ color: '#5eddac' }}>交易详情</TableCell>
                      <TableCell align="right" sx={{ color: '#5eddac' }}>盈亏</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {symbolTransactions.records.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell sx={{ color: '#fff' }}>{record.transaction_time}</TableCell>
                        <TableCell sx={{ color: '#999' }}>{record.transaction_result}</TableCell>
                        <TableCell 
                          align="right" 
                          sx={{ 
                            color: record.transaction_pnl >= 0 ? '#5eddac' : '#ff6b6b',
                            fontWeight: 'bold'
                          }}
                        >
                          ${record.transaction_pnl}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid #5eddac20' }}>
          <Button onClick={handleCloseSymbolDetail} sx={{ color: '#5eddac' }}>
            关闭
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BacktestDetail; 