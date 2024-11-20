// components/PositionTable.js
import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Paper,
    Box,
    Typography,
    Chip
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { formatNumber, formatPrice } from '../utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
    tableContainer: {
        marginTop: theme.spacing(2),
    },
    longChip: {
        backgroundColor: theme.palette.success.main,
        color: theme.palette.common.white,
    },
    shortChip: {
        backgroundColor: theme.palette.error.main,
        color: theme.palette.common.white,
    },
    profitText: {
        color: theme.palette.success.main,
    },
    lossText: {
        color: theme.palette.error.main,
    },
    noDataText: {
        padding: theme.spacing(3),
        textAlign: 'center',
        color: theme.palette.text.secondary,
    }
}));

export const PositionTable = ({ ccy }) => {
    const classes = useStyles();

    // Mock data - 替换为实际API数据
    const positions = [
        {
            id: 1,
            side: 'long',
            size: '0.5',
            avgPrice: '42000',
            markPrice: '43000',
            margin: '1000',
            leverage: '10',
            unrealizedPnl: '+420',
            unrealizedPnlPercentage: '+2.5',
            liquidationPrice: '38000'
        },
        {
            id: 2,
            side: 'short',
            size: '0.3',
            avgPrice: '41500',
            markPrice: '41000',
            margin: '800',
            leverage: '5',
            unrealizedPnl: '-150',
            unrealizedPnlPercentage: '-1.2',
            liquidationPrice: '45000'
        }
    ];

    if (!positions.length) {
        return (
            <Typography variant="body2" className={classes.noDataText}>
                暂无持仓
            </Typography>
        );
    }

    return (
        <Paper className={classes.tableContainer}>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>方向</TableCell>
                        <TableCell align="right">仓位大小</TableCell>
                        <TableCell align="right">杠杆</TableCell>
                        <TableCell align="right">开仓均价</TableCell>
                        <TableCell align="right">标记价格</TableCell>
                        <TableCell align="right">未实现盈亏</TableCell>
                        <TableCell align="right">保证金</TableCell>
                        <TableCell align="right">强平价格</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {positions.map((position) => (
                        <TableRow key={position.id}>
                            <TableCell>
                                <Chip
                                    label={position.side === 'long' ? '多' : '空'}
                                    size="small"
                                    className={position.side === 'long' ? classes.longChip : classes.shortChip}
                                />
                            </TableCell>
                            <TableCell align="right">
                                {formatNumber(position.size)}
                            </TableCell>
                            <TableCell align="right">
                                {position.leverage}x
                            </TableCell>
                            <TableCell align="right">
                                {formatPrice(position.avgPrice)}
                            </TableCell>
                            <TableCell align="right">
                                {formatPrice(position.markPrice)}
                            </TableCell>
                            <TableCell align="right">
                                <Box display="flex" flexDirection="column" alignItems="flex-end">
                                    <Typography
                                        variant="body2"
                                        className={
                                            position.unrealizedPnl.startsWith('+')
                                                ? classes.profitText
                                                : classes.lossText
                                        }
                                    >
                                        {position.unrealizedPnl} USDT
                                    </Typography>
                                    <Typography
                                        variant="caption"
                                        className={
                                            position.unrealizedPnlPercentage.startsWith('+')
                                                ? classes.profitText
                                                : classes.lossText
                                        }
                                    >
                                        {position.unrealizedPnlPercentage}%
                                    </Typography>
                                </Box>
                            </TableCell>
                            <TableCell align="right">
                                {position.margin} USDT
                            </TableCell>
                            <TableCell align="right">
                                {formatPrice(position.liquidationPrice)}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
};