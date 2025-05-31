import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Alert,
  Checkbox,
  ListItemText,
  OutlinedInput,
  CircularProgress,
  Pagination
} from '@mui/material';
import {
  Add,
  Refresh,
  Info,
  Assessment,
  TrendingUp,
  SwapHoriz,
  ShowChart,
  Timer,
  Delete
} from '@mui/icons-material';
import http from '../api/http';
import { useNavigate } from 'react-router-dom';

// CSS样式定义
const styles = `
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 169, 77, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 169, 77, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 169, 77, 0);
  }
}
`;

// 注入样式
const injectStyles = () => {
  const styleElement = document.createElement('style');
  styleElement.textContent = styles;
  document.head.appendChild(styleElement);
  return () => document.head.removeChild(styleElement);
};

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
    sx: {
      background: '#23272a',
      color: '#fff',
      '& .MuiMenuItem-root': { color: '#fff' },
    },
  },
};

const BacktestInterface = () => {
  const navigate = useNavigate();
  const [backtestRecords, setBacktestRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  // 分页相关
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [total, setTotal] = useState(0);
  
  // 策略和交易对
  const [entryStrategies, setEntryStrategies] = useState([]);
  const [exitStrategies, setExitStrategies] = useState([]);
  const [filterStrategies, setFilterStrategies] = useState([]);
  const [availableSymbols, setAvailableSymbols] = useState([]);

  // 新回测配置
  const [newBacktest, setNewBacktest] = useState({
    entryStrategy: '',
    exitStrategy: '',
    filterStrategy: '',
    symbols: [],
    timeframe: '4h',
    backtestPeriod: '1m', // 1m, 3m, 1y
    initialCash: 100000,
    riskPercent: 2.0,
    commission: 0.001
  });

  // 加载回测记录
  const loadBacktestRecords = async (pageNum = page) => {
    setLoading(true);
    try {
      const response = await http.get(`/api/enhanced-backtest/records?page=${pageNum}&page_size=${pageSize}`);
      if (response.data.success) {
        setBacktestRecords(response.data.records || []);
        setTotal(response.data.total || 0);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('加载回测记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载策略列表
  const loadStrategies = async () => {
    try {
      const response = await http.get('/api/enhanced-backtest/strategies');
      if (response.data.success) {
        setEntryStrategies(response.data.strategies.entry || []);
        setExitStrategies(response.data.strategies.exit || []);
        setFilterStrategies(response.data.strategies.filter || []);
      }
    } catch (error) {
      console.error('Load strategies error:', error);
    }
  };

  // 加载交易对列表
  const loadSymbols = async () => {
    try {
      const response = await http.get('/api/enhanced-backtest/symbols');
      if (response.data.success) {
        setAvailableSymbols(response.data.symbols || []);
      }
    } catch (error) {
      console.error('Load symbols error:', error);
    }
  };

  // 注入CSS样式
  useEffect(() => {
    const cleanup = injectStyles();
    return cleanup;
  }, []);

  // 自动刷新hook
  useEffect(() => {
    // 检查是否有运行中的回测
    const hasRunningBacktests = backtestRecords.some(record => 
      record.status === 'running' || record.status === 'analyzing'
    );
    
    if (hasRunningBacktests) {
      const interval = setInterval(() => {
        loadBacktestRecords();
      }, 30000); // 每30秒刷新一次
      
      return () => clearInterval(interval);
    }
  }, [backtestRecords]);

  useEffect(() => {
    loadBacktestRecords(page);
    loadStrategies();
    loadSymbols();
  }, [page]);

  // 创建回测
  const handleCreateBacktest = async () => {
    try {
      setIsRunning(true);
      const requestData = {
        entry_strategy: newBacktest.entryStrategy,
        exit_strategy: newBacktest.exitStrategy,
        filter_strategy: newBacktest.filterStrategy || null,
        symbols: newBacktest.symbols,
        timeframe: newBacktest.timeframe,
        backtest_period: newBacktest.backtestPeriod,
        initial_cash: newBacktest.initialCash,
        risk_percent: newBacktest.riskPercent,
        commission: newBacktest.commission,
        save_to_db: true,
        description: '前端创建的回测'
      };

      const response = await http.post('/api/enhanced-backtest/run', requestData);
      
      if (response.data.success) {
        setCreateDialogOpen(false);
        // 立即加载回测记录以显示新创建的记录
        loadBacktestRecords();
        // 重置表单
        setNewBacktest({
          entryStrategy: '',
          exitStrategy: '',
          filterStrategy: '',
          symbols: [],
          timeframe: '4h',
          backtestPeriod: '1m',
          initialCash: 100000,
          riskPercent: 2.0,
          commission: 0.001
        });
        // 显示成功消息
        setError(null);
        alert(`回测已开始执行，记录ID: ${response.data.record_id}`);
      } else {
        setError(response.data.error || '回测创建失败');
      }
    } catch (error) {
      console.error('Create backtest error:', error);
      setError(error.response?.data?.detail || '创建回测失败');
    } finally {
      setIsRunning(false);
    }
  };

  // 查看详情
  const handleViewDetails = (recordId) => {
    navigate(`/enhanced-backtest/${recordId}`);
  };

  // 删除回测记录
  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm('确定要删除这条回测记录吗？')) {
      return;
    }
    
    try {
      const response = await http.delete(`/api/enhanced-backtest/record/${recordId}`);
      if (response.data.success) {
        loadBacktestRecords();
      } else {
        setError(response.data.error || '删除失败');
      }
    } catch (error) {
      setError('删除回测记录失败');
    }
  };

  // 获取状态颜色
  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return '#ffa94d';
      case 'analyzing':
        return '#5eddac';
      case 'completed':
        return '#5eddac';
      case 'failed':
        return '#ff6b6b';
      default:
        return '#ccc';
    }
  };

  // 获取状态文本
  const getStatusText = (status) => {
    switch (status) {
      case 'running':
        return '运行中';
      case 'analyzing':
        return '分析中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      default:
        return '未知';
    }
  };

  // 获取回测时间段文本
  const getPeriodText = (period) => {
    const today = new Date('2025-06-01'); // 假设今天为2025年6月1日
    let startDate;
    
    switch (period) {
      case '1m':
        startDate = new Date(today);
        startDate.setMonth(startDate.getMonth() - 1);
        break;
      case '3m':
        startDate = new Date(today);
        startDate.setMonth(startDate.getMonth() - 3);
        break;
      case '1y':
        startDate = new Date(today);
        startDate.setFullYear(startDate.getFullYear() - 1);
        break;
      default:
        return period;
    }
    
    const formatDate = (date) => {
      return date.toISOString().split('T')[0]; // yyyy-MM-dd format
    };
    
    return `${formatDate(startDate)} ~ ${formatDate(today)}`;
  };

  // 格式化策略组合
  const formatStrategyCombo = (record) => {
    return (
      <Box sx={{ lineHeight: 1.2 }}>
        <div>{record.entry_strategy}</div>
        <div>/{record.exit_strategy}</div>
        {record.filter_strategy && <div>/{record.filter_strategy}</div>}
      </Box>
    );
  };

  // 格式化运行时间
  const formatRunTime = (startTime, endTime) => {
    if (!startTime || !endTime) return '-';
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = Math.floor((end - start) / 1000); // 秒
    if (diff < 60) return `${diff}秒`;
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟`;
    return `${Math.floor(diff / 3600)}小时`;
  };

  // 分页切换
  const handlePageChange = (event, value) => {
    setPage(value);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center' }}>
            <Assessment sx={{ mr: 1, color: '#5eddac' }} />
            策略回测
            {/* 运行状态指示器 */}
            {backtestRecords.filter(r => r.status === 'running' || r.status === 'analyzing').length > 0 && (
              <Chip 
                label={`${backtestRecords.filter(r => r.status === 'running' || r.status === 'analyzing').length} 个运行中`}
                size="small"
                sx={{ 
                  ml: 2,
                  background: '#ffa94d',
                  color: '#181c1f',
                  fontWeight: 600,
                  animation: 'pulse 2s infinite'
                }}
              />
            )}
      </Typography>
          <Typography variant="body2" sx={{ color: '#ccc', mt: 1 }}>
            测试策略组合的历史表现
            {backtestRecords.filter(r => r.status === 'running' || r.status === 'analyzing').length > 0 && (
              <span style={{ color: '#ffa94d', marginLeft: '8px' }}>
                • 自动刷新中 (30秒)
              </span>
            )}
      </Typography>
        </Box>
        <Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ background: '#5eddac', color: '#181c1f', fontWeight: 600, mr: 2 }}
          >
            创建回测
          </Button>
          <IconButton 
            onClick={loadBacktestRecords} 
            sx={{ color: '#5eddac' }}
            title="手动刷新"
          >
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 统计卡片 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Assessment sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">{backtestRecords.length}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>总回测数</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ShowChart sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">
                    {backtestRecords.filter(r => r.status === 'running').length}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>运行中</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">
                    {backtestRecords.filter(r => r.total_return > 0).length}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>盈利策略</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Timer sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">
                    {Math.max(...backtestRecords.map(r => r.win_rate || 0)).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>最高胜率</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 回测记录列表 */}
      <TableContainer component={Paper} sx={{ background: '#181c1f' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '60px' }}>ID</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '150px' }}>策略组合</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '180px' }}>交易对</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '80px' }}>频率</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '100px' }}>状态</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '200px' }}>回测时间段</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600, width: '100px' }}>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <CircularProgress sx={{ color: '#5eddac' }} />
                </TableCell>
              </TableRow>
            ) : backtestRecords.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ color: '#ccc', py: 4 }}>
                  暂无回测记录
                </TableCell>
              </TableRow>
            ) : (
              backtestRecords.map((record) => (
                <TableRow key={record.id} hover>
                  <TableCell sx={{ color: '#fff' }}>{record.id}</TableCell>
                  <TableCell sx={{ color: '#fff', fontSize: '12px', maxWidth: '150px' }}>
                    {formatStrategyCombo(record)}
                  </TableCell>
                  <TableCell sx={{ color: '#fff', fontSize: '13px' }}>
                    {record.symbols ? record.symbols.join(', ') : ''}
                  </TableCell>
                  <TableCell sx={{ color: '#fff' }}>{record.timeframe}</TableCell>
                  <TableCell>
                    <Chip 
                      label={getStatusText(record.status)} 
                      size="small"
                      sx={{ 
                        background: getStatusColor(record.status), 
                        color: '#181c1f',
                        fontWeight: 600 
                      }} 
                    />
                  </TableCell>
                  <TableCell sx={{ color: '#fff' }}>
                    {getPeriodText(record.backtest_period)}
                  </TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      onClick={() => handleViewDetails(record.id)} 
                      sx={{ color: '#5eddac' }}
                    >
                      <Info />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => handleDeleteRecord(record.id)} 
                      sx={{ color: '#ff6b6b' }}
                      disabled={record.status === 'running' || record.status === 'analyzing'}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 分页控件 */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
        {total > pageSize && (
          <Pagination
            count={Math.ceil(total / pageSize)}
            page={page}
            onChange={handlePageChange}
            sx={{
              '& .MuiPaginationItem-root': {
                color: '#ccc',
                '&.Mui-selected': {
                  background: '#5eddac',
                  color: '#181c1f'
                }
              }
            }}
          />
        )}
      </Box>

      {/* 创建回测对话框 */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { background: '#23272a', color: '#fff' }
        }}
      >
        <DialogTitle>创建回测</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>入场策略</InputLabel>
                <Select
                  value={newBacktest.entryStrategy}
                  onChange={(e) => setNewBacktest({ ...newBacktest, entryStrategy: e.target.value })}
                  sx={{ 
                    color: '#fff',
                    '& .MuiFilledInput-root': {
                      background: '#23272a',
                      '&:hover': { background: '#2a2f33' },
                      '&.Mui-focused': { background: '#23272a' }
                    },
                    '& .MuiSelect-icon': { color: '#5eddac' },
                    '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                    '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                    '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                  }}
                  MenuProps={MenuProps}
                >
                  {entryStrategies.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      {strategy.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>出场策略</InputLabel>
                <Select
                  value={newBacktest.exitStrategy}
                  onChange={(e) => setNewBacktest({ ...newBacktest, exitStrategy: e.target.value })}
                  sx={{ 
                    color: '#fff',
                    '& .MuiFilledInput-root': {
                      background: '#23272a',
                      '&:hover': { background: '#2a2f33' },
                      '&.Mui-focused': { background: '#23272a' }
                    },
                    '& .MuiSelect-icon': { color: '#5eddac' },
                    '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                    '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                    '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                  }}
                  MenuProps={MenuProps}
                >
                  {exitStrategies.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      {strategy.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>过滤策略（可选）</InputLabel>
                <Select
                  value={newBacktest.filterStrategy}
                  onChange={(e) => setNewBacktest({ ...newBacktest, filterStrategy: e.target.value })}
                  sx={{ 
                    color: '#fff',
                    '& .MuiFilledInput-root': {
                      background: '#23272a',
                      '&:hover': { background: '#2a2f33' },
                      '&.Mui-focused': { background: '#23272a' }
                    },
                    '& .MuiSelect-icon': { color: '#5eddac' },
                    '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                    '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                    '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                  }}
                  MenuProps={MenuProps}
                >
                  <MenuItem value="">无</MenuItem>
                  {filterStrategies.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      {strategy.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>交易对（可多选）</InputLabel>
                <Select
                  multiple
                  value={newBacktest.symbols}
                  onChange={(e) => setNewBacktest({ ...newBacktest, symbols: e.target.value })}
                  input={<OutlinedInput label="交易对" />}
                  renderValue={(selected) => selected.join(', ')}
                  MenuProps={MenuProps}
                  sx={{ 
                    color: '#fff',
                    '& .MuiOutlinedInput-root': {
                      background: '#23272a',
                      '&:hover': { background: '#2a2f33' },
                      '&.Mui-focused': { background: '#23272a' },
                      '& fieldset': { borderColor: '#333' },
                      '&:hover fieldset': { borderColor: '#5eddac' },
                      '&.Mui-focused fieldset': { borderColor: '#5eddac' }
                    },
                    '& .MuiSelect-icon': { color: '#5eddac' }
                  }}
                >
                  {availableSymbols.map((symbol) => (
                    <MenuItem key={symbol} value={symbol}>
                      <Checkbox checked={newBacktest.symbols.indexOf(symbol) > -1} sx={{ color: '#5eddac' }} />
                      <ListItemText primary={symbol} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>时间窗口</InputLabel>
                <Select
                  value={newBacktest.timeframe}
                  onChange={(e) => setNewBacktest({ ...newBacktest, timeframe: e.target.value })}
                  sx={{ 
                    color: '#fff',
                    '& .MuiFilledInput-root': {
                      background: '#23272a',
                      '&:hover': { background: '#2a2f33' },
                      '&.Mui-focused': { background: '#23272a' }
                    },
                    '& .MuiSelect-icon': { color: '#5eddac' },
                    '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                    '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                    '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                  }}
                  MenuProps={MenuProps}
                >
                  <MenuItem value="1h">1小时</MenuItem>
                  <MenuItem value="4h">4小时</MenuItem>
                  <MenuItem value="1d">1天</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>回测时间段</InputLabel>
                <Select
                  value={newBacktest.backtestPeriod}
                  onChange={(e) => setNewBacktest({ ...newBacktest, backtestPeriod: e.target.value })}
                sx={{ 
                    color: '#fff',
                  '& .MuiFilledInput-root': {
                    background: '#23272a',
                    '&:hover': { background: '#2a2f33' },
                    '&.Mui-focused': { background: '#23272a' }
                  },
                    '& .MuiSelect-icon': { color: '#5eddac' },
                  '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                  '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                  '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                }}
                  MenuProps={MenuProps}
                >
                  <MenuItem value="1m">最近一月</MenuItem>
                  <MenuItem value="3m">最近三月</MenuItem>
                  <MenuItem value="1y">最近一年</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)} sx={{ color: '#ccc' }}>
            取消
          </Button>
          <Button 
            onClick={handleCreateBacktest} 
            variant="contained"
            disabled={isRunning || !newBacktest.entryStrategy || !newBacktest.exitStrategy || newBacktest.symbols.length === 0}
            sx={{ background: '#5eddac', color: '#181c1f', fontWeight: 600 }}
          >
            {isRunning ? <CircularProgress size={20} /> : '开始回测'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BacktestInterface; 