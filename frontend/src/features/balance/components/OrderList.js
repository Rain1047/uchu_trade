import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Chip,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { formatNumber, formatPrice } from '../utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
  stopLossChip: {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.error.contrastText,
  },
  limitOrderChip: {
    backgroundColor: theme.palette.success.main,
    color: theme.palette.success.contrastText,
  },
  noDataText: {
    padding: theme.spacing(3),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  statusChip: {
    backgroundColor: theme.palette.info.main,
    color: theme.palette.common.white,
  }
}));

export const OrderList = ({ orders }) => {
  const classes = useStyles();

  if (!orders?.length) {
    return (
      <Typography variant="body2" className={classes.noDataText}>
        暂无委托数据
      </Typography>
    );
  }

  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>类型</TableCell>
          <TableCell align="right">数量</TableCell>
          <TableCell align="right">目标价格</TableCell>
          <TableCell align="right">金额(USDT)</TableCell>
          <TableCell>状态</TableCell>
          <TableCell>创建时间</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {orders.map((order) => (
          <TableRow key={order.id}>
            <TableCell>
              <Chip
                label={order.type === 'stop_loss' ? '止损卖出' : '限价买入'}
                size="small"
                className={order.type === 'stop_loss' ? classes.stopLossChip : classes.limitOrderChip}
              />
            </TableCell>
            <TableCell align="right">{formatNumber(order.sz)}</TableCell>
            <TableCell align="right">{formatPrice(order.target_price)}</TableCell>
            <TableCell align="right">{formatNumber(order.amount)}</TableCell>
            <TableCell>
              <Chip
                label={order.status === 'live' ? '生效中' : '已成交'}
                size="small"
                className={classes.statusChip}
              />
            </TableCell>
            <TableCell>{order.create_time}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};