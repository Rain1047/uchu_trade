import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  OutlinedInput,
  ListItemText,
  Checkbox
} from '@mui/material';
import {
  PlayArrow,
  Refresh,
  TrendingUp,
  SwapHoriz,
  GpsFixed,
  AccountBalance,
  ExpandMore,
  Settings,
  Assessment,
  Info
} from '@mui/icons-material';
import axios from 'axios';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const BacktestInterface = () => {
  // 状态管理
  const [isRunning, setIsRunning] = useState(false);
  const [entryStrategies, setEntryStrategies] = useState([]);
  const [exitStrategies, setExitStrategies] = useState([]);
  const [filterStrategies, setFilterStrategies] = useState([]);
  const [availableSymbols, setAvailableSymbols] = useState([]);
  const [backtestResult, setBacktestResult] = useState(null);
  const [error, setError] = useState(null);

  // 回测配置
  const [config, setConfig] = useState({
    entryStrategy: '',
    exitStrategy: '',
    filterStrategy: '',
    symbols: [],
    timeframe: '4h',
    initialCash: 100000,
    riskPercent: 2.0,
    commission: 0.001
  });

  // 加载策略列表
  const loadStrategies = async () => {
    try {
      const response = await axios.get('/api/enhanced-backtest/strategies');
      if (response.data.success) {
        setEntryStrategies(response.data.strategies.entry || []);
        setExitStrategies(response.data.strategies.exit || []);
        setFilterStrategies(response.data.strategies.filter || []);
      }
    } catch (error) {
      setError('加载策略列表失败');
      console.error('Load strategies error:', error);
    }
  };

  // 加载交易对列表
  const loadSymbols = async () => {
    try {
      const response = await axios.get('/api/enhanced-backtest/symbols');
      if (response.data.success) {
        setAvailableSymbols(response.data.symbols || []);
      }
    } catch (error) {
      setError('加载交易对列表失败');
      console.error('Load symbols error:', error);
    }
  };

  // 运行回测
  const runBacktest = async () => {
    if (!canRunBacktest()) {
      setError('请完善回测配置');
      return;
    }

    setIsRunning(true);
    setBacktestResult(null);
    setError(null);

    try {
      const requestData = {
        entry_strategy: config.entryStrategy,
        exit_strategy: config.exitStrategy,
        filter_strategy: config.filterStrategy || null,
        symbols: config.symbols,
        timeframe: config.timeframe,
        initial_cash: config.initialCash,
        risk_percent: config.riskPercent,
        commission: config.commission,
        save_to_db: true,
        description: 'React前端界面回测'
      };

      const response = await axios.post('/api/enhanced-backtest/run', requestData);
      
      if (response.data.success) {
        setBacktestResult(response.data);
        // 滚动到结果区域
        setTimeout(() => {
          const resultElement = document.getElementById('backtest-results');
          if (resultElement) {
            resultElement.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
      } else {
        setError(response.data.error || '回测失败');
      }
    } catch (error) {
      setError('回测请求失败');
      console.error('Backtest error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  // 重置配置
  const resetConfig = () => {
    setConfig({
      entryStrategy: '',
      exitStrategy: '',
      filterStrategy: '',
      symbols: [],
      timeframe: '4h',
      initialCash: 100000,
      riskPercent: 2.0,
      commission: 0.001
    });
    setBacktestResult(null);
    setError(null);
  };

  // 检查是否可以运行回测
  const canRunBacktest = () => {
    return config.entryStrategy && 
           config.exitStrategy && 
           config.symbols.length > 0 && 
           config.timeframe &&
           !isRunning;
  };

  // 格式化百分比
  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return (value * 100).toFixed(2) + '%';
  };

  // 格式化日期时间
  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('zh-CN');
  };

  // 获取收益率颜色
  const getReturnColor = (value) => {
    if (value > 0) return 'success';
    if (value < 0) return 'error';
    return 'default';
  };

  // 处理配置变化
  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 处理多选交易对变化
  const handleSymbolChange = (event) => {
    const value = event.target.value;
    setConfig(prev => ({
      ...prev,
      symbols: typeof value === 'string' ? value.split(',') : value
    }));
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadStrategies();
    loadSymbols();
  }, []);

  return (
    <Box sx={{ p: 3, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* 页面标题 */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
          <Assessment sx={{ mr: 2, fontSize: 'inherit' }} />
          智能回测系统
        </Typography>
        <Typography variant="h6" color="text.secondary">
          选择策略组合，配置参数，一键运行回测
        </Typography>
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 配置面板 */}
      <Card sx={{ mb: 4, borderRadius: 2 }}>
        <CardHeader
          avatar={<Settings color="primary" />}
          title="回测配置"
          titleTypographyProps={{ variant: 'h5', fontWeight: 600 }}
        />
        <CardContent>
          <Grid container spacing={3}>
            {/* 策略选择 */}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>入场策略</InputLabel>
                <Select
                  value={config.entryStrategy}
                  label="入场策略"
                  onChange={(e) => handleConfigChange('entryStrategy', e.target.value)}
                >
                  {entryStrategies.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      <Box>
                        <Typography variant="body1">{strategy.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {strategy.desc}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>出场策略</InputLabel>
                <Select
                  value={config.exitStrategy}
                  label="出场策略"
                  onChange={(e) => handleConfigChange('exitStrategy', e.target.value)}
                >
                  {exitStrategies.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      <Box>
                        <Typography variant="body1">{strategy.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {strategy.desc}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>过滤策略（可选）</InputLabel>
                <Select
                  value={config.filterStrategy}
                  label="过滤策略（可选）"
                  onChange={(e) => handleConfigChange('filterStrategy', e.target.value)}
                >
                  <MenuItem value="">
                    <em>无</em>
                  </MenuItem>
                  {filterStrategies.map((strategy) => (
                    <MenuItem key={strategy.name} value={strategy.name}>
                      <Box>
                        <Typography variant="body1">{strategy.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {strategy.desc}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* 交易对和时间窗口 */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>交易对（可多选）</InputLabel>
                <Select
                  multiple
                  value={config.symbols}
                  onChange={handleSymbolChange}
                  input={<OutlinedInput label="交易对（可多选）" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  MenuProps={MenuProps}
                >
                  {availableSymbols.map((symbol) => (
                    <MenuItem key={symbol} value={symbol}>
                      <Checkbox checked={config.symbols.indexOf(symbol) > -1} />
                      <ListItemText primary={symbol} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>时间窗口</InputLabel>
                <Select
                  value={config.timeframe}
                  label="时间窗口"
                  onChange={(e) => handleConfigChange('timeframe', e.target.value)}
                >
                  <MenuItem value="1h">1小时</MenuItem>
                  <MenuItem value="4h">4小时</MenuItem>
                  <MenuItem value="1d">1天</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* 回测参数 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="初始资金"
                type="number"
                value={config.initialCash}
                onChange={(e) => handleConfigChange('initialCash', Number(e.target.value))}
                InputProps={{ inputProps: { min: 1000, max: 10000000, step: 1000 } }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="风险百分比 (%)"
                type="number"
                value={config.riskPercent}
                onChange={(e) => handleConfigChange('riskPercent', Number(e.target.value))}
                InputProps={{ inputProps: { min: 0.1, max: 10, step: 0.1 } }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="手续费率"
                type="number"
                value={config.commission}
                onChange={(e) => handleConfigChange('commission', Number(e.target.value))}
                InputProps={{ inputProps: { min: 0, max: 0.01, step: 0.0001 } }}
              />
            </Grid>

            {/* 操作按钮 */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 2 }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={isRunning ? <CircularProgress size={20} /> : <PlayArrow />}
                  onClick={runBacktest}
                  disabled={!canRunBacktest()}
                  sx={{ px: 4, py: 1.5 }}
                >
                  {isRunning ? '回测中...' : '开始回测'}
                </Button>
                
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<Refresh />}
                  onClick={resetConfig}
                  sx={{ px: 4, py: 1.5 }}
                >
                  重置配置
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 结果展示 */}
      {backtestResult && (
        <Box id="backtest-results">
          {/* 整体表现卡片 */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUp sx={{ fontSize: 40, mr: 2 }} />
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {formatPercent(backtestResult.summary.avg_return)}
                      </Typography>
                      <Typography variant="body2">平均收益率</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SwapHoriz sx={{ fontSize: 40, mr: 2 }} />
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {backtestResult.summary.total_trades_all}
                      </Typography>
                      <Typography variant="body2">总交易次数</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <GpsFixed sx={{ fontSize: 40, mr: 2 }} />
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {formatPercent(backtestResult.summary.avg_win_rate / 100)}
                      </Typography>
                      <Typography variant="body2">平均胜率</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AccountBalance sx={{ fontSize: 40, mr: 2 }} />
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {backtestResult.summary.total_symbols}
                      </Typography>
                      <Typography variant="body2">测试交易对</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* 详细结果表格 */}
          <Card sx={{ mb: 4, borderRadius: 2 }}>
            <CardHeader
              avatar={<Assessment color="primary" />}
              title="详细回测结果"
              titleTypographyProps={{ variant: 'h5', fontWeight: 600 }}
              action={
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {backtestResult.summary.best_symbol && (
                    <Chip label={`最佳: ${backtestResult.summary.best_symbol}`} color="success" size="small" />
                  )}
                  {backtestResult.summary.worst_symbol && (
                    <Chip label={`最差: ${backtestResult.summary.worst_symbol}`} color="error" size="small" />
                  )}
                </Box>
              }
            />
            <CardContent>
              <TableContainer component={Paper} sx={{ borderRadius: 1 }}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell sx={{ fontWeight: 600 }}>交易对</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>收益率</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>年化收益率</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>夏普比率</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>最大回撤</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>交易次数</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>胜率</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>入场信号</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>信号执行率</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>测试天数</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {backtestResult.summary.individual_results.map((row) => (
                      <TableRow key={row.symbol} hover>
                        <TableCell>
                          <Chip label={row.symbol} variant="outlined" size="small" />
                        </TableCell>
                        <TableCell>
                          <Typography color={getReturnColor(row.total_return)} sx={{ fontWeight: 600 }}>
                            {formatPercent(row.total_return)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography color={getReturnColor(row.annual_return)} sx={{ fontWeight: 600 }}>
                            {formatPercent(row.annual_return)}
                          </Typography>
                        </TableCell>
                        <TableCell>{row.sharpe_ratio ? row.sharpe_ratio.toFixed(2) : 'N/A'}</TableCell>
                        <TableCell>
                          <Typography color="error" sx={{ fontWeight: 600 }}>
                            {formatPercent(row.max_drawdown)}
                          </Typography>
                        </TableCell>
                        <TableCell>{row.total_trades}</TableCell>
                        <TableCell>{formatPercent(row.win_rate / 100)}</TableCell>
                        <TableCell>{row.total_entry_signals}</TableCell>
                        <TableCell>{formatPercent(row.signal_execution_rate / 100)}</TableCell>
                        <TableCell>{row.duration_days}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* 配置信息 */}
          <Card sx={{ borderRadius: 2 }}>
            <CardHeader
              avatar={<Info color="primary" />}
              title="回测配置信息"
              titleTypographyProps={{ variant: 'h5', fontWeight: 600 }}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">策略组合</Typography>
                  <Typography variant="body1">{backtestResult.report['配置信息']['策略组合']}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">时间框架</Typography>
                  <Typography variant="body1">{backtestResult.report['配置信息']['时间框架']}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">初始资金</Typography>
                  <Typography variant="body1">{backtestResult.report['配置信息']['初始资金']}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">风险百分比</Typography>
                  <Typography variant="body1">{backtestResult.report['配置信息']['风险百分比']}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">手续费</Typography>
                  <Typography variant="body1">{backtestResult.report['配置信息']['手续费']}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">测试时间</Typography>
                  <Typography variant="body1">{formatDateTime(backtestResult.report['配置信息']['测试时间'])}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default BacktestInterface; 