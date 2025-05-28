import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  Alert
} from '@mui/material';
import {
  ArrowBack,
  TrendingUp,
  Schedule,
  SwapHoriz,
  CheckCircle,
  Error,
  HourglassEmpty
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import http from '../api/http';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const StrategyInstanceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [instance, setInstance] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 加载实例详情
  const loadInstanceDetail = async () => {
    try {
      const [instanceRes, executionsRes] = await Promise.all([
        http.get(`/api/strategy-instance/${id}`),
        http.get(`/api/strategy-instance/${id}/executions`)
      ]);

      if (instanceRes.data.success) {
        setInstance(instanceRes.data.instance);
      } else {
        setError(instanceRes.data.error);
      }

      if (executionsRes.data.success) {
        setExecutions(executionsRes.data.executions);
      }
    } catch (err) {
      setError('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInstanceDetail();
  }, [id]);

  // 准备图表数据
  const prepareChartData = () => {
    return executions.map((exec, index) => ({
      name: `执行${index + 1}`,
      profit: exec.total_profit,
      profitRate: exec.profit_rate * 100,
      trades: exec.total_trades,
      winRate: exec.metrics?.win_rate || 0
    })).reverse();
  };

  // 获取执行状态颜色
  const getExecutionStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#5eddac';
      case 'failed':
        return '#ff6b6b';
      case 'running':
        return '#ffa94d';
      default:
        return '#ccc';
    }
  };

  // 获取执行状态图标
  const getExecutionStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle sx={{ fontSize: 20, color: '#5eddac' }} />;
      case 'failed':
        return <Error sx={{ fontSize: 20, color: '#ff6b6b' }} />;
      case 'running':
        return <HourglassEmpty sx={{ fontSize: 20, color: '#ffa94d' }} />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Container>
        <Typography>加载中...</Typography>
      </Container>
    );
  }

  if (!instance) {
    return (
      <Container>
        <Typography>实例不存在</Typography>
      </Container>
    );
  }

  const chartData = prepareChartData();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 返回按钮和标题 */}
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/strategy-instance')}
          sx={{ mb: 2, color: '#5eddac' }}
        >
          返回列表
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 600, color: '#fff' }}>
          {instance.strategy_name}
        </Typography>
        <Typography variant="body2" sx={{ color: '#ccc', mt: 1 }}>
          {instance.strategy_params.entry_strategy} / {instance.strategy_params.exit_strategy}
          {instance.strategy_params.filter_strategy && ` / ${instance.strategy_params.filter_strategy}`}
        </Typography>
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 概览卡片 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{instance.status}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>状态</Typography>
                </Box>
                <Schedule sx={{ fontSize: 40, color: '#5eddac' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{instance.total_executions}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>执行次数</Typography>
                </Box>
                <SwapHoriz sx={{ fontSize: 40, color: '#5eddac' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{instance.total_trades}</Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>总交易次数</Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: '#5eddac' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: '#23272a', color: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography 
                    variant="h6" 
                    sx={{ color: instance.total_profit >= 0 ? '#5eddac' : '#ff6b6b' }}
                  >
                    {instance.total_profit.toFixed(2)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc' }}>总收益</Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: '#5eddac' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 图表区域 */}
      {chartData.length > 0 && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ background: '#23272a', color: '#fff', p: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>收益趋势</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#ccc" />
                  <YAxis stroke="#ccc" />
                  <Tooltip 
                    contentStyle={{ background: '#23272a', border: '1px solid #333' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="profit" 
                    stroke="#5eddac" 
                    strokeWidth={2}
                    name="收益"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="profitRate" 
                    stroke="#ffa94d" 
                    strokeWidth={2}
                    name="收益率(%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ background: '#23272a', color: '#fff', p: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>交易统计</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#ccc" />
                  <YAxis stroke="#ccc" />
                  <Tooltip 
                    contentStyle={{ background: '#23272a', border: '1px solid #333' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Bar dataKey="trades" fill="#5eddac" name="交易次数" />
                  <Bar dataKey="winRate" fill="#ffa94d" name="胜率(%)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 执行记录表格 */}
      <Card sx={{ background: '#23272a', color: '#fff' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>执行记录</Typography>
          <TableContainer component={Paper} sx={{ background: '#181c1f' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>执行时间</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>状态</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>交易次数</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>成功/失败</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>收益</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>收益率</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>夏普比率</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>最大回撤</TableCell>
                  <TableCell sx={{ color: '#fff', fontWeight: 600 }}>胜率</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {executions.map((exec) => (
                  <TableRow key={exec.id} hover>
                    <TableCell sx={{ color: '#fff' }}>
                      {exec.execution_time}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getExecutionStatusIcon(exec.status)}
                        <Typography sx={{ color: getExecutionStatusColor(exec.status) }}>
                          {exec.status}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ color: '#fff' }}>{exec.total_trades}</TableCell>
                    <TableCell sx={{ color: '#fff' }}>
                      {exec.successful_trades}/{exec.failed_trades}
                    </TableCell>
                    <TableCell sx={{ 
                      color: exec.total_profit >= 0 ? '#5eddac' : '#ff6b6b',
                      fontWeight: 600 
                    }}>
                      {exec.total_profit.toFixed(2)}
                    </TableCell>
                    <TableCell sx={{ 
                      color: exec.profit_rate >= 0 ? '#5eddac' : '#ff6b6b',
                      fontWeight: 600 
                    }}>
                      {(exec.profit_rate * 100).toFixed(2)}%
                    </TableCell>
                    <TableCell sx={{ color: '#fff' }}>
                      {exec.metrics?.sharpe_ratio?.toFixed(2) || '-'}
                    </TableCell>
                    <TableCell sx={{ color: '#ff6b6b' }}>
                      {exec.metrics?.max_drawdown 
                        ? `${(exec.metrics.max_drawdown * 100).toFixed(2)}%`
                        : '-'}
                    </TableCell>
                    <TableCell sx={{ color: '#fff' }}>
                      {exec.metrics?.win_rate?.toFixed(2) || '-'}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* 策略配置信息 */}
      <Card sx={{ background: '#23272a', color: '#fff', mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>策略配置</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#ccc' }}>执行频率</Typography>
              <Typography variant="body1">{instance.schedule_frequency}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#ccc' }}>每笔入场资金</Typography>
              <Typography variant="body1">
                {instance.entry_per_trans ? `${instance.entry_per_trans} USDT` : '-'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#ccc' }}>每笔最大损失</Typography>
              <Typography variant="body1">
                {instance.loss_per_trans ? `${instance.loss_per_trans} USDT` : '-'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" sx={{ color: '#ccc' }}>手续费率</Typography>
              <Typography variant="body1">{instance.commission}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" sx={{ color: '#ccc' }}>交易对</Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                {instance.symbols.map((symbol) => (
                  <Chip 
                    key={symbol} 
                    label={symbol} 
                    size="small"
                    sx={{ background: '#5eddac', color: '#181c1f', fontWeight: 600 }}
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default StrategyInstanceDetail; 