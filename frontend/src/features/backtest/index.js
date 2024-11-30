import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  ButtonGroup,
  Grid,
  Divider
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(3),
  },
  paper: {
    backgroundColor: '#222',
    padding: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
  controls: {
    display: 'flex',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  formControl: {
    minWidth: 120,
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: '#444',
      },
      '&:hover fieldset': {
        borderColor: '#666',
      },
    },
  },
  buttonGroup: {
    '& .MuiButton-root': {
      color: '#fff',
      borderColor: '#444',
      '&.active': {
        backgroundColor: '#5eddac',
        color: '#000',
      },
    },
  },
  plotContainer: {
    position: 'relative',
    height: 400,
    margin: theme.spacing(4),
    backgroundColor: '#1a1a1a',
    borderRadius: theme.shape.borderRadius,
  },
  axisContainer: {
    position: 'absolute',
    left: 60,
    right: 20,
    top: 20,
    bottom: 40,
    borderLeft: '1px solid #444',
    borderBottom: '1px solid #444',
  },
  point: {
    position: 'absolute',
    width: 6,
    height: 6,
    borderRadius: '50%',
    transform: 'translate(-50%, -50%)',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    '&:hover': {
      width: 8,
      height: 8,
      zIndex: 2,
    },
  },
  profitPoint: {
    backgroundColor: '#5eddac',
  },
  lossPoint: {
    backgroundColor: '#f57ad0',
  },
  tooltip: {
    position: 'absolute',
    backgroundColor: '#333',
    border: '1px solid #444',
    padding: theme.spacing(1),
    borderRadius: 4,
    fontSize: 12,
    pointerEvents: 'none',
    zIndex: 1000,
  },
  yAxis: {
    position: 'absolute',
    left: -50,
    top: 0,
    bottom: 0,
    width: 40,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    color: '#888',
    fontSize: 12,
  },
  xAxis: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: -30,
    display: 'flex',
    justifyContent: 'space-between',
    color: '#888',
    fontSize: 12,
  },
  centerLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: '50%',
    borderTop: '1px dashed #444',
  },
  statsContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: theme.spacing(3),
    marginTop: theme.spacing(3),
    padding: theme.spacing(2),
    backgroundColor: '#1a1a1a',
    borderRadius: theme.shape.borderRadius,
  },
  statItem: {
    textAlign: 'center',
  },
  advancedStats: {
    marginTop: theme.spacing(3),
  },
  advancedStatsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: theme.spacing(2),
  },
  advancedStatCard: {
    backgroundColor: '#1a1a1a',
    padding: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
  }
}));

const BacktestResults = () => {
  const classes = useStyles();
  const [tooltipData, setTooltipData] = useState(null);
  const [timeframe, setTimeframe] = useState('1M');
  const [symbol, setSymbol] = useState('BTC-USDT');
  const [view, setView] = useState('trades');

  // Mock data generators
  const generateMockData = (days) => {
    const data = [];
    const now = new Date();
    for(let i = 0; i < days; i++) {
      const date = new Date(now - i * 24 * 60 * 60 * 1000);
      data.push({
        date,
        value: Math.random() > 0.5 ? Math.random() * 400 : -Math.random() * 300,
        trades: Math.floor(Math.random() * 5) + 1
      });
    }
    return data.reverse();
  };

  const data = generateMockData(30);

  const maxValue = Math.max(...data.map(d => Math.abs(d.value))) * 1.2;
  const minDate = Math.min(...data.map(d => d.date.getTime()));
  const maxDate = Math.max(...data.map(d => d.date.getTime()));

  const getXPosition = (date) => {
    return ((date.getTime() - minDate) / (maxDate - minDate)) * 100 + '%';
  };

  const getYPosition = (value) => {
    return (50 - (value / maxValue) * 50) + '%';
  };

  // Calculate advanced metrics
  const calculateMetrics = () => {
    const profits = data.filter(d => d.value > 0).map(d => d.value);
    const losses = data.filter(d => d.value < 0).map(d => d.value);

    return {
      totalTrades: data.length,
      winRate: ((profits.length / data.length) * 100).toFixed(1),
      avgWin: (profits.reduce((a, b) => a + b, 0) / profits.length).toFixed(2),
      avgLoss: (Math.abs(losses.reduce((a, b) => a + b, 0)) / losses.length).toFixed(2),
      profitFactor: (profits.reduce((a, b) => a + b, 0) / Math.abs(losses.reduce((a, b) => a + b, 0))).toFixed(2),
      maxDrawdown: (Math.min(...data.map(d => d.value))).toFixed(2),
      sharpeRatio: '1.85',
      maxConsecutiveWins: 4,
      maxConsecutiveLosses: 3,
    };
  };

  const metrics = calculateMetrics();

  return (
    <Container className={classes.root}>
      <Paper className={classes.paper}>
        <Typography variant="h5" gutterBottom>回测结果分析</Typography>

        <Box className={classes.controls}>
          <FormControl variant="outlined" className={classes.formControl}>
            <InputLabel>交易对</InputLabel>
            <Select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              label="交易对"
            >
              <MenuItem value="BTC-USDT">BTC-USDT</MenuItem>
              <MenuItem value="ETH-USDT">ETH-USDT</MenuItem>
              <MenuItem value="BNB-USDT">BNB-USDT</MenuItem>
            </Select>
          </FormControl>

          <ButtonGroup variant="outlined" className={classes.buttonGroup}>
            <Button
              className={timeframe === '1W' ? 'active' : ''}
              onClick={() => setTimeframe('1W')}
            >
              1周
            </Button>
            <Button
              className={timeframe === '1M' ? 'active' : ''}
              onClick={() => setTimeframe('1M')}
            >
              1月
            </Button>
            <Button
              className={timeframe === '3M' ? 'active' : ''}
              onClick={() => setTimeframe('3M')}
            >
              3月
            </Button>
          </ButtonGroup>

          <ButtonGroup variant="outlined" className={classes.buttonGroup}>
            <Button
              className={view === 'trades' ? 'active' : ''}
              onClick={() => setView('trades')}
            >
              交易视图
            </Button>
            <Button
              className={view === 'equity' ? 'active' : ''}
              onClick={() => setView('equity')}
            >
              权益曲线
            </Button>
          </ButtonGroup>
        </Box>

        <div className={classes.plotContainer}>
          <div className={classes.axisContainer}>
            <div className={classes.centerLine} />

            {data.map((point, index) => (
              <div
                key={index}
                className={`${classes.point} ${point.value >= 0 ? classes.profitPoint : classes.lossPoint}`}
                style={{
                  left: getXPosition(point.date),
                  top: getYPosition(point.value),
                }}
                onMouseEnter={(e) => setTooltipData({
                  x: e.clientX,
                  y: e.clientY,
                  data: point
                })}
                onMouseLeave={() => setTooltipData(null)}
              />
            ))}

            <div className={classes.yAxis}>
              <span>${maxValue.toFixed(0)}</span>
              <span>0</span>
              <span>-${maxValue.toFixed(0)}</span>
            </div>

            <div className={classes.xAxis}>
              <span>{new Date(minDate).toLocaleDateString()}</span>
              <span>{new Date(maxDate).toLocaleDateString()}</span>
            </div>
          </div>

          {tooltipData && (
            <div className={classes.tooltip} style={{
              left: tooltipData.x + 10,
              top: tooltipData.y - 40
            }}>
              <div>日期: {tooltipData.data.date.toLocaleDateString()}</div>
              <div>收益: ${tooltipData.data.value.toFixed(2)}</div>
              <div>交易数: {tooltipData.data.trades}</div>
            </div>
          )}
        </div>

        <Box className={classes.statsContainer}>
          <Box className={classes.statItem}>
            <Typography variant="h6" color="primary">${metrics.totalTrades * 100}</Typography>
            <Typography color="textSecondary">总收益</Typography>
          </Box>
          <Box className={classes.statItem}>
            <Typography variant="h6" color="primary">{metrics.winRate}%</Typography>
            <Typography color="textSecondary">胜率</Typography>
          </Box>
          <Box className={classes.statItem}>
            <Typography variant="h6" color="primary">{metrics.totalTrades}</Typography>
            <Typography color="textSecondary">交易次数</Typography>
          </Box>
          <Box className={classes.statItem}>
            <Typography variant="h6" color="primary">${metrics.avgWin}</Typography>
            <Typography color="textSecondary">平均收益</Typography>
          </Box>
        </Box>

        <Box className={classes.advancedStats}>
          <Typography variant="h6" gutterBottom>详细指标</Typography>
          <Divider style={{ margin: '16px 0' }} />
          <Box className={classes.advancedStatsGrid}>
            <Paper className={classes.advancedStatCard}>
              <Typography color="textSecondary" gutterBottom>盈利能力</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">平均盈利</Typography>
                  <Typography variant="body1">${metrics.avgWin}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">平均亏损</Typography>
                  <Typography variant="body1">${metrics.avgLoss}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">利润因子</Typography>
                  <Typography variant="body1">{metrics.profitFactor}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">夏普比率</Typography>
                  <Typography variant="body1">{metrics.sharpeRatio}</Typography>
                </Grid>
              </Grid>
            </Paper>

            <Paper className={classes.advancedStatCard}>
              <Typography color="textSecondary" gutterBottom>风险控制</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">最大回撤</Typography>
                  <Typography variant="body1">${Math.abs(metrics.maxDrawdown)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">最大连续盈利</Typography>
                  <Typography variant="body1">{metrics.maxConsecutiveWins}次</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">最大连续亏损</Typography>
                  <Typography variant="body1">{metrics.maxConsecutiveLosses}次</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">盈亏比</Typography>
                  <Typography variant="body1">{(metrics.avgWin / metrics.avgLoss).toFixed(2)}</Typography>
                </Grid>
              </Grid>
            </Paper>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default BacktestResults;