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
  Pagination
} from '@mui/material';
import {
  ArrowBack,
  TrendingUp,
  TrendingDown,
  ShowChart,
  SwapHoriz,
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';
import http from '../api/http';
import { useNavigate, useParams } from 'react-router-dom';

const BacktestDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backtestData, setBacktestData] = useState(null);
  const [sortBy, setSortBy] = useState('win_rate');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // 加载回测详情
  const loadBacktestDetail = async () => {
    setLoading(true);
    try {
      const response = await http.get(`/api/enhanced-backtest/record/${id}`);
      if (response.data.success) {
        setBacktestData(response.data.data);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('加载回测详情失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBacktestDetail();
  }, [id]);

  // 排序数据
  const getSortedData = () => {
    if (!backtestData || !backtestData.symbol_results) return [];
    
    const sorted = [...backtestData.symbol_results].sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortOrder === 'desc') {
        return bValue - aValue;
      } else {
        return aValue - bValue;
      }
    });
    
    // 分页
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return sorted.slice(startIndex, endIndex);
  };

  // 处理排序
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setPage(1);
  };

  // 计算总结数据
  const getSummaryData = () => {
    if (!backtestData || !backtestData.symbol_results) return null;
    
    const results = backtestData.symbol_results;
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

  const summary = getSummaryData();
  const sortedData = getSortedData();
  const totalPages = backtestData ? Math.ceil(backtestData.symbol_results.length / pageSize) : 0;

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress sx={{ color: '#5eddac' }} />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
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
              {backtestData.entry_strategy}/{backtestData.exit_strategy}
              {backtestData.filter_strategy && `/${backtestData.filter_strategy}`}
              {' - '}
              {backtestData.timeframe}
            </Typography>
          )}
        </Box>
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 总结卡片 */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ background: '#23272a', color: '#fff' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ShowChart sx={{ fontSize: 32, mr: 1, color: '#5eddac' }} />
                  <Box>
                    <Typography variant="h6">{summary.totalSymbols}</Typography>
                    <Typography variant="body2" sx={{ color: '#ccc' }}>回测交易对数</Typography>
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
                    <Typography variant="h6">{summary.profitableSymbols}</Typography>
                    <Typography variant="body2" sx={{ color: '#ccc' }}>盈利个数</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ background: '#23272a', color: '#fff' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingDown sx={{ fontSize: 32, mr: 1, color: '#ff6b6b' }} />
                  <Box>
                    <Typography variant="h6">{summary.losingSymbols}</Typography>
                    <Typography variant="body2" sx={{ color: '#ccc' }}>亏损个数</Typography>
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
                    <Typography variant="h6">{summary.avgWinRate.toFixed(1)}%</Typography>
                    <Typography variant="body2" sx={{ color: '#ccc' }}>总胜率</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 排序选项 */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
        <Typography variant="body2" sx={{ color: '#ccc', mr: 2 }}>排序：</Typography>
        <ToggleButtonGroup
          value={sortBy}
          exclusive
          onChange={(e, value) => value && handleSort(value)}
          size="small"
          sx={{ 
            '& .MuiToggleButton-root': { 
              color: '#ccc',
              borderColor: '#333',
              '&.Mui-selected': {
                color: '#181c1f',
                background: '#5eddac'
              }
            }
          }}
        >
          <ToggleButton value="win_rate">
            胜率 {sortBy === 'win_rate' && (sortOrder === 'desc' ? <ArrowDownward sx={{ ml: 0.5, fontSize: 16 }} /> : <ArrowUpward sx={{ ml: 0.5, fontSize: 16 }} />)}
          </ToggleButton>
          <ToggleButton value="profit_loss_ratio">
            盈亏比 {sortBy === 'profit_loss_ratio' && (sortOrder === 'desc' ? <ArrowDownward sx={{ ml: 0.5, fontSize: 16 }} /> : <ArrowUpward sx={{ ml: 0.5, fontSize: 16 }} />)}
          </ToggleButton>
          <ToggleButton value="total_profit">
            总盈利 {sortBy === 'total_profit' && (sortOrder === 'desc' ? <ArrowDownward sx={{ ml: 0.5, fontSize: 16 }} /> : <ArrowUpward sx={{ ml: 0.5, fontSize: 16 }} />)}
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* 详细数据表格 */}
      <TableContainer component={Paper} sx={{ background: '#181c1f', mb: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>交易对</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>交易次数</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>盈利次数</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>亏损次数</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>胜率</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>平均单笔盈利</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>平均单笔亏损</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>盈亏比</TableCell>
              <TableCell sx={{ color: '#fff', fontWeight: 600 }}>总盈利</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedData.map((row) => (
              <TableRow key={row.symbol} hover>
                <TableCell sx={{ color: '#fff' }}>{row.symbol}</TableCell>
                <TableCell sx={{ color: '#fff' }}>{row.total_trades}</TableCell>
                <TableCell sx={{ color: '#5eddac' }}>{row.winning_trades}</TableCell>
                <TableCell sx={{ color: '#ff6b6b' }}>{row.losing_trades}</TableCell>
                <TableCell sx={{ color: '#fff' }}>
                  {row.win_rate ? `${row.win_rate.toFixed(1)}%` : '0%'}
                </TableCell>
                <TableCell sx={{ color: '#5eddac' }}>
                  {row.avg_win ? `$${row.avg_win.toFixed(2)}` : '$0'}
                </TableCell>
                <TableCell sx={{ color: '#ff6b6b' }}>
                  {row.avg_loss ? `$${Math.abs(row.avg_loss).toFixed(2)}` : '$0'}
                </TableCell>
                <TableCell sx={{ color: '#fff' }}>
                  {row.profit_loss_ratio ? row.profit_loss_ratio.toFixed(2) : '-'}
                </TableCell>
                <TableCell sx={{ 
                  color: row.total_profit >= 0 ? '#5eddac' : '#ff6b6b',
                  fontWeight: 600
                }}>
                  ${row.total_profit.toFixed(2)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 分页 */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <Pagination 
            count={totalPages} 
            page={page} 
            onChange={(e, value) => setPage(value)}
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
        </Box>
      )}
    </Container>
  );
};

export default BacktestDetail; 