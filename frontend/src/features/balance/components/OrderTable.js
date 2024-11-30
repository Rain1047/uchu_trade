// components/OrderTable.js
import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Paper,
    Typography,
    Chip,
    IconButton,
    Tooltip
} from '@material-ui/core';
import { Cancel as CancelIcon } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import { formatNumber, formatPrice } from '../utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
    tableContainer: {
        marginTop: theme.spacing(2),
    },
    buyChip: {
        backgroundColor: theme.palette.success.main,
        color: theme.palette.common.white,
    },
    sellChip: {
        backgroundColor: theme.palette.error.main,
        color: theme.palette.common.white,
    },
    limitChip: {
        backgroundColor: theme.palette.info.main,
        color: theme.palette.common.white,
    },
    stopChip: {
        backgroundColor: theme.palette.warning.main,
        color: theme.palette.common.white,
    },
    noDataText: {
        padding: theme.spacing(3),
        textAlign: 'center',
        color: theme.palette.text.secondary,
    },
    cancelButton: {
        padding: 4,
    }
}));

export const OrderTable = ({ ccy }) => {
    const classes = useStyles();

    // Mock data - 替换为实际API数据
    const orders = [
        {
            id: 1,
            type: 'limit',
            side: 'buy',
            price: '43000',
            size: '0.2',
            filled: '0',
            status: 'active',
            createTime: '2024-02-20 10:30:00'
        },
        {
            id: 2,
            type: 'stop',
            side: 'sell',
            price: '41000',
            size: '0.3',
            filled: '0',
            status: 'active',
            createTime: '2024-02-20 11:15:00'
        }
    ];

    const handleCancelOrder = (orderId) => {
        console.log('Cancel order:', orderId);
        // 实现取消订单的逻辑
    };

    if (!orders.length) {
        return (
            <Typography variant="body2" className={classes.noDataText}>
                暂无活动委托
            </Typography>
        );
    }

    const getOrderTypeChip = (type) => {
        return (
            <Chip
                label={type === 'limit' ? '限价' : '止损'}
                size="small"
                className={type === 'limit' ? classes.limitChip : classes.stopChip}
            />
        );
    };

    const getOrderSideChip = (side) => {
        return (
            <Chip
                label={side === 'buy' ? '买入' : '卖出'}
                size="small"
                className={side === 'buy' ? classes.buyChip : classes.sellChip}
            />
        );
    };

    return (
        <Paper className={classes.tableContainer}>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>类型</TableCell>
                        <TableCell>方向</TableCell>
                        <TableCell align="right">价格</TableCell>
                        <TableCell align="right">数量</TableCell>
                        <TableCell align="right">已成交</TableCell>
                        <TableCell>状态</TableCell>
                        <TableCell>下单时间</TableCell>
                        <TableCell align="center">操作</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {orders.map((order) => (
                        <TableRow key={order.id}>
                            <TableCell>
                                {getOrderTypeChip(order.type)}
                            </TableCell>
                            <TableCell>
                                {getOrderSideChip(order.side)}
                            </TableCell>
                            <TableCell align="right">
                                {formatPrice(order.price)}
                            </TableCell>
                            <TableCell align="right">
                                {formatNumber(order.size)}
                            </TableCell>
                            <TableCell align="right">
                                {formatNumber(order.filled)}
                            </TableCell>
                            <TableCell>
                                <Chip
                                    label={order.status === 'active' ? '活动' : '其他'}
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                />
                            </TableCell>
                            <TableCell>
                                {order.createTime}
                            </TableCell>
                            <TableCell align="center">
                                <Tooltip title="撤销订单">
                                    <IconButton
                                        className={classes.cancelButton}
                                        size="small"
                                        onClick={() => handleCancelOrder(order.id)}
                                    >
                                        <CancelIcon fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
};