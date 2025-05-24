import React, { useMemo } from 'react';
import { Paper, Typography, Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import dayjs from 'dayjs';

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
    marginTop: theme.spacing(3)
  },
  chartBox: {
    width: '100%',
    height: 300,
    marginBottom: theme.spacing(4)
  },
  title: {
    marginBottom: theme.spacing(1)
  }
}));

export default function BacktestChart({ records = [] }) {
  const classes = useStyles();

  const { cumulativeData, tradeData } = useMemo(() => {
    let cumulative = 0;
    const cumArray = [];
    const tradeArray = [];

    records.forEach((rec, idx) => {
      const pnlNum = parseFloat(rec.transaction_pnl) || 0;
      const pnl = Number(pnlNum.toFixed(2));
      cumulative = Number((cumulative + pnl).toFixed(2));
      const dateStr = dayjs(rec.transaction_time).format('YY/MM/DD');

      cumArray.push({ idx: idx + 1, date: dateStr, cumulative });
      tradeArray.push({
        idx: idx + 1,
        date: dateStr,
        pnl,
        // 颜色：盈利绿，亏损红
        fill: pnl >= 0 ? '#4caf50' : '#f44336'
      });
    });
    return { cumulativeData: cumArray, tradeData: tradeArray };
  }, [records]);

  if (!records.length) return null;

  const tooltipFormatter = (val) => Number(val).toFixed(2);

  return (
    <Paper className={classes.root} elevation={3}>
      <Typography variant="h6" className={classes.title}>
        回测盈亏分析
      </Typography>

      {/* 累计收益曲线 */}
      <Box className={classes.chartBox}>
        <Typography variant="subtitle2">累计收益曲线</Typography>
        <ResponsiveContainer>
          <LineChart data={cumulativeData} margin={{ top: 20, right: 30, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="idx" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => v.toFixed(0)} />
            <Tooltip formatter={tooltipFormatter} labelFormatter={(l) => `交易 #${l}`} />
            <Line type="monotone" dataKey="cumulative" stroke="#2196f3" dot={false} name="累计收益" />
          </LineChart>
        </ResponsiveContainer>
      </Box>

      {/* 单笔盈亏柱状图 */}
      <Box className={classes.chartBox}>
        <Typography variant="subtitle2">单笔交易盈亏</Typography>
        <ResponsiveContainer>
          <BarChart data={tradeData} margin={{ top: 20, right: 30, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="idx" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => v.toFixed(0)} />
            <Tooltip formatter={tooltipFormatter} labelFormatter={(l) => `交易 #${l}`} />
            <Bar dataKey="pnl" name="盈亏">
              {tradeData.map((d, i) => (
                <Cell key={i} fill={d.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}

export { BacktestChart };