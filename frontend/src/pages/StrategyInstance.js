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
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Alert,
  Checkbox,
  ListItemText,
  OutlinedInput
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Delete,
  Add,
  Refresh,
  Info,
  Schedule,
  TrendingUp,
  SwapHoriz
} from '@mui/icons-material';
import http from '../api/http';
import { useNavigate } from 'react-router-dom';

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

const StrategyInstance = () => {
  const navigate = useNavigate();
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [strategies, setStrategies] = useState({ entry: [], exit: [], filter: [] });
  const [symbols, setSymbols] = useState([]);
  const [newInstance, setNewInstance] = useState({
    strategy_name: '',
    entry_strategy: '',
    exit_strategy: '',
    filter_strategy: '',
    schedule_frequency: '4h',
    symbols: [],
    entry_per_trans: '',
    loss_per_trans: '',
    commission: 0.001
  });

  // 加载实例列表
  const loadInstances = async () => {
    setLoading(true);
    try {
      const response = await http.get('/api/strategy-instance/list');
      if (response.data.success) {
        setInstances(response.data.instances);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('加载策略实例失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载策略和交易对
  const loadStrategiesAndSymbols = async () => {
    try {
      // 加载策略
      const strategyResponse = await http.get('/api/enhanced-backtest/strategies');
      if (strategyResponse.data.success) {
        setStrategies(strategyResponse.data.strategies);
      }

      // 加载交易对
      const symbolResponse = await http.get('/api/enhanced-backtest/symbols');
      if (symbolResponse.data.success) {
        setSymbols(symbolResponse.data.symbols);
      }
    } catch (err) {
      console.error('加载策略和交易对失败:', err);
    }
  };

  useEffect(() => {
    loadInstances();
    loadStrategiesAndSymbols();
  }, []);

  // 创建实例
  const handleCreate = async () => {
    try {
      const response = await http.post('/api/strategy-instance/create', newInstance);
      if (response.data.success) {
        setCreateDialogOpen(false);
        loadInstances();
        setNewInstance({
          strategy_name: '',
          entry_strategy: '',
          exit_strategy: '',
          filter_strategy: '',
          schedule_frequency: '4h',
          symbols: [],
          entry_per_trans: '',
          loss_per_trans: '',
          commission: 0.001
        });
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('创建策略实例失败');
    }
  };

  // 启动实例
  const handleStart = async (instanceId) => {
    try {
      const response = await http.post(`/api/strategy-instance/${instanceId}/start`);
      if (response.data.success) {
        loadInstances();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('启动策略实例失败');
    }
  };

  // 停止实例
  const handleStop = async (instanceId) => {
    try {
      const response = await http.post(`/api/strategy-instance/${instanceId}/stop`);
      if (response.data.success) {
        loadInstances();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('停止策略实例失败');
    }
  };

  // 暂停实例
  const handlePause = async (instanceId) => {
    try {
      const response = await http.post(`/api/strategy-instance/${instanceId}/pause`);
      if (response.data.success) {
        loadInstances();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('暂停策略实例失败');
    }
  };

  // 恢复实例
  const handleResume = async (instanceId) => {
    try {
      const response = await http.post(`/api/strategy-instance/${instanceId}/resume`);
      if (response.data.success) {
        loadInstances();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('恢复策略实例失败');
    }
  };

  // 删除实例
  const handleDelete = async (instanceId) => {
    if (window.confirm('确定要删除这个策略实例吗？')) {
      try {
        const response = await http.delete(`/api/strategy-instance/${instanceId}`);
        if (response.data.success) {
          loadInstances();
        } else {
          setError(response.data.error);
        }
      } catch (err) {
        setError('删除策略实例失败');
      }
    }
  };

  // 查看详情
  const handleViewDetails = (instanceId) => {
    navigate(`/strategy-instance/${instanceId}`);
  };

  // 获取状态颜色
  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return '#5eddac';
      case 'stopped':
        return '#ff6b6b';
      case 'paused':
        return '#ffa94d';
      default:
        return '#ccc';
    }
  };

  // 获取状态文本
  const getStatusText = (status) => {
    switch (status) {
      case 'running':
        return '运行中';
      case 'stopped':
        return '已停止';
      case 'paused':
        return '已暂停';
      default:
        return '未知';
    }
  };

  // 筛选实例
  const filteredInstances = instances.filter(instance => {
    if (tabValue === 0) return true;
    if (tabValue === 1) return instance.status === 'running';
    if (tabValue === 2) return instance.status === 'stopped';
    if (tabValue === 3) return instance.status === 'paused';
    return true;
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center' }}>
            <Schedule sx={{ mr: 1, color: '#5eddac' }} />
            策略实例管理
          </Typography>
          <Typography variant="body2" sx={{ color: '#ccc', mt: 1 }}>
            管理和监控自动运行的策略实例
          </Typography>
        </Box>
        <Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ background: '#5eddac', color: '#181c1f', fontWeight: 600, mr: 2 }}
          >
            创建实例
          </Button>
          <IconButton onClick={loadInstances} sx={{ color: '#5eddac' }}>
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
                <Schedule sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">{instances.length}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>总实例数</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PlayArrow sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">{instances.filter(i => i.status === 'running').length}</Typography>
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
                  <Typography variant="h6">{instances.reduce((sum, i) => sum + i.total_trades, 0)}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>总交易次数</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SwapHoriz sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                <Box>
                  <Typography variant="h6">{instances.reduce((sum, i) => sum + i.total_profit, 0).toFixed(2)}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>总收益</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 标签页 */}
      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label={`全部 (${instances.length})`} />
        <Tab label={`运行中 (${instances.filter(i => i.status === 'running').length})`} />
        <Tab label={`已停止 (${instances.filter(i => i.status === 'stopped').length})`} />
        <Tab label={`已暂停 (${instances.filter(i => i.status === 'paused').length})`} />
      </Tabs>

      {/* 实例列表 */}
      <TableContainer component={Paper} sx={{ background: '#181c1f' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>策略名称</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>策略组合</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>频率</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>状态</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>下次执行</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>执行次数</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>总交易</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>总收益</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>胜率</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredInstances.map((instance) => (
              <TableRow key={instance.id} hover>
                <TableCell sx={{ color: '#fff' }}>{instance.strategy_name}</TableCell>
                <TableCell sx={{ color: '#fff' }}>
                  <Typography variant="caption">
                    入场: {instance.strategy_params.entry_strategy}<br />
                    出场: {instance.strategy_params.exit_strategy}<br />
                    {instance.strategy_params.filter_strategy && 
                      `过滤: ${instance.strategy_params.filter_strategy}`}
                  </Typography>
                </TableCell>
                <TableCell sx={{ color: '#fff' }}>{instance.schedule_frequency}</TableCell>
                <TableCell>
                  <Chip 
                    label={getStatusText(instance.status)} 
                    size="small"
                    sx={{ 
                      background: getStatusColor(instance.status), 
                      color: '#181c1f',
                      fontWeight: 600 
                    }} 
                  />
                </TableCell>
                <TableCell sx={{ color: '#fff' }}>
                  {instance.next_execution_time || '-'}
                </TableCell>
                <TableCell sx={{ color: '#fff' }}>{instance.total_executions}</TableCell>
                <TableCell sx={{ color: '#fff' }}>{instance.total_trades}</TableCell>
                <TableCell sx={{ color: instance.total_profit >= 0 ? '#5eddac' : '#ff6b6b', fontWeight: 600 }}>
                  {instance.total_profit.toFixed(2)}
                </TableCell>
                <TableCell sx={{ color: '#fff' }}>
                  {instance.win_rate ? `${instance.win_rate.toFixed(2)}%` : '-'}
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {instance.status === 'stopped' && (
                      <IconButton size="small" onClick={() => handleStart(instance.id)} sx={{ color: '#5eddac' }}>
                        <PlayArrow />
                      </IconButton>
                    )}
                    {instance.status === 'running' && (
                      <>
                        <IconButton size="small" onClick={() => handlePause(instance.id)} sx={{ color: '#ffa94d' }}>
                          <Pause />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleStop(instance.id)} sx={{ color: '#ff6b6b' }}>
                          <Stop />
                        </IconButton>
                      </>
                    )}
                    {instance.status === 'paused' && (
                      <>
                        <IconButton size="small" onClick={() => handleResume(instance.id)} sx={{ color: '#5eddac' }}>
                          <PlayArrow />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleStop(instance.id)} sx={{ color: '#ff6b6b' }}>
                          <Stop />
                        </IconButton>
                      </>
                    )}
                    <IconButton size="small" onClick={() => handleViewDetails(instance.id)} sx={{ color: '#5eddac' }}>
                      <Info />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(instance.id)} sx={{ color: '#ff6b6b' }}>
                      <Delete />
                    </IconButton>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 创建实例对话框 */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { background: '#23272a', color: '#fff' }
        }}
      >
        <DialogTitle>创建策略实例</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="策略名称"
                value={newInstance.strategy_name}
                onChange={(e) => setNewInstance({ ...newInstance, strategy_name: e.target.value })}
                variant="filled"
                sx={{ 
                  background: '#181c1f',
                  '& .MuiInputBase-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#aaa' }
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>入场策略</InputLabel>
                <Select
                  value={newInstance.entry_strategy}
                  onChange={(e) => setNewInstance({ ...newInstance, entry_strategy: e.target.value })}
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
                  {strategies.entry.map((strategy) => (
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
                  value={newInstance.exit_strategy}
                  onChange={(e) => setNewInstance({ ...newInstance, exit_strategy: e.target.value })}
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
                  {strategies.exit.map((strategy) => (
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
                  value={newInstance.filter_strategy}
                  onChange={(e) => setNewInstance({ ...newInstance, filter_strategy: e.target.value })}
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
                  {strategies.filter.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      {strategy.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>执行频率</InputLabel>
                <Select
                  value={newInstance.schedule_frequency}
                  onChange={(e) => setNewInstance({ ...newInstance, schedule_frequency: e.target.value })}
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
                  <MenuItem value="5m">5分钟</MenuItem>
                  <MenuItem value="15m">15分钟</MenuItem>
                  <MenuItem value="1h">1小时</MenuItem>
                  <MenuItem value="4h">4小时</MenuItem>
                  <MenuItem value="1d">1天</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="filled" sx={{ background: '#181c1f' }}>
                <InputLabel sx={{ color: '#aaa' }}>交易对</InputLabel>
                <Select
                  multiple
                  value={newInstance.symbols}
                  onChange={(e) => setNewInstance({ ...newInstance, symbols: e.target.value })}
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
                  {symbols.map((symbol) => (
                    <MenuItem key={symbol} value={symbol}>
                      <Checkbox checked={newInstance.symbols.indexOf(symbol) > -1} sx={{ color: '#5eddac' }} />
                      <ListItemText primary={symbol} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="每笔入场资金 (USDT)"
                type="number"
                value={newInstance.entry_per_trans}
                onChange={(e) => setNewInstance({ 
                  ...newInstance, 
                  entry_per_trans: e.target.value,
                  loss_per_trans: '' // 清空另一个字段
                })}
                disabled={newInstance.loss_per_trans !== ''}
                variant="filled"
                sx={{ 
                  background: '#181c1f',
                  '& .MuiInputBase-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#aaa' },
                  '& .MuiFilledInput-root': {
                    background: '#23272a',
                    '&:hover': { background: '#2a2f33' },
                    '&.Mui-focused': { background: '#23272a' }
                  },
                  '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                  '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                  '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="每笔最大损失 (USDT)"
                type="number"
                value={newInstance.loss_per_trans}
                onChange={(e) => setNewInstance({ 
                  ...newInstance, 
                  loss_per_trans: e.target.value,
                  entry_per_trans: '' // 清空另一个字段
                })}
                disabled={newInstance.entry_per_trans !== ''}
                variant="filled"
                sx={{ 
                  background: '#181c1f',
                  '& .MuiInputBase-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#aaa' },
                  '& .MuiFilledInput-root': {
                    background: '#23272a',
                    '&:hover': { background: '#2a2f33' },
                    '&.Mui-focused': { background: '#23272a' }
                  },
                  '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                  '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                  '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="手续费率"
                type="number"
                value={newInstance.commission}
                onChange={(e) => setNewInstance({ ...newInstance, commission: Number(e.target.value) })}
                variant="filled"
                sx={{ 
                  background: '#181c1f',
                  '& .MuiInputBase-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#aaa' },
                  '& .MuiFilledInput-root': {
                    background: '#23272a',
                    '&:hover': { background: '#2a2f33' },
                    '&.Mui-focused': { background: '#23272a' }
                  },
                  '& .MuiFilledInput-underline:before': { borderBottomColor: '#333' },
                  '& .MuiFilledInput-underline:hover:before': { borderBottomColor: '#5eddac' },
                  '& .MuiFilledInput-underline:after': { borderBottomColor: '#5eddac' }
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)} sx={{ color: '#ccc' }}>
            取消
          </Button>
          <Button 
            onClick={handleCreate} 
            variant="contained"
            sx={{ background: '#5eddac', color: '#181c1f', fontWeight: 600 }}
          >
            创建
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default StrategyInstance; 