import React, { useState } from 'react';
import {
    Container,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Switch,
    Collapse,
    Box,
    Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { green, blue } from '@material-ui/core/colors';
import AutoTradeConfig from './components/AutoTradeConfig';
import { useBalance } from './hooks/useBalance';
import { TABLE_COLUMNS } from './constants/balanceConstants';
import { calculatePrice, formatNumber, formatBalance } from './utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        marginTop: theme.spacing(3),
    },
    table: {
        minWidth: 650,
    },
    stopLossConfig: {
        backgroundColor: green[50],
        '&:hover': {
            backgroundColor: green[100],
        }
    },
    limitConfig: {
        backgroundColor: blue[50],
        '&:hover': {
            backgroundColor: blue[100],
        }
    },
    emptyState: {
        padding: theme.spacing(3),
        textAlign: 'center',
        color: theme.palette.text.secondary,
    },
    loading: {
        padding: theme.spacing(3),
        textAlign: 'center',
    },
    error: {
        padding: theme.spacing(3),
        textAlign: 'center',
        color: theme.palette.error.main,
    }
}));

const BalanceList = () => {
    const classes = useStyles();
    const [expandedRows, setExpandedRows] = useState({});
    const { assets, loading, error, saveAutoConfig } = useBalance();

    const handleToggle = (ccy, type) => {
        setExpandedRows(prev => ({
            ...prev,
            [ccy]: {
                ...prev[ccy],
                [type]: !prev[ccy]?.[type]
            }
        }));
    };

    if (loading) {
        return (
            <Container className={classes.root}>
                <Typography variant="h5" gutterBottom>
                    资产管理
                </Typography>
                <Paper className={classes.loading}>
                    <Typography>Loading...</Typography>
                </Paper>
            </Container>
        );
    }

    if (error) {
        return (
            <Container className={classes.root}>
                <Typography variant="h5" gutterBottom>
                    资产管理
                </Typography>
                <Paper className={classes.error}>
                    <Typography>Error: {error}</Typography>
                </Paper>
            </Container>
        );
    }

    if (!assets || assets.length === 0) {
        return (
            <Container className={classes.root}>
                <Typography variant="h5" gutterBottom>
                    资产管理
                </Typography>
                <Paper className={classes.emptyState}>
                    <Typography>暂无资产数据</Typography>
                </Paper>
            </Container>
        );
    }

    return (
        <Container className={classes.root}>
            <Typography variant="h5" gutterBottom>
                资产管理
            </Typography>

            <TableContainer component={Paper}>
                <Table className={classes.table}>
                    <TableHead>
                        <TableRow>
                            {TABLE_COLUMNS.map(column => (
                                <TableCell key={column.id} align={column.align}>
                                    {column.label}
                                </TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {assets.map((asset) => (
                            <React.Fragment key={asset.ccy}>
                                <TableRow hover>
                                    <TableCell>{asset.ccy}</TableCell>
                                    <TableCell align="right">
                                        {formatBalance(asset.avail_bal)}
                                    </TableCell>
                                    <TableCell align="right">
                                        {formatNumber(asset.eq_usd)}
                                    </TableCell>
                                    <TableCell align="right">
                                        {calculatePrice(asset.eq_usd, asset.avail_bal)}
                                    </TableCell>
                                    <TableCell align="right">
                                        {formatNumber(asset.acc_avg_px)}
                                    </TableCell>
                                    <TableCell align="center">
                                        <Switch
                                            checked={asset.stop_loss_switch === 'true'}
                                            onChange={() => handleToggle(asset.ccy, 'stop_loss')}
                                            color="primary"
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Switch
                                            checked={asset.limit_order_switch === 'true'}
                                            onChange={() => handleToggle(asset.ccy, 'limit')}
                                            color="primary"
                                        />
                                    </TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell colSpan={7} style={{ paddingBottom: 0, paddingTop: 0 }}>
                                        <Collapse
                                            in={expandedRows[asset.ccy]?.stop_loss}
                                            timeout="auto"
                                            unmountOnExit
                                        >
                                            <Box className={classes.stopLossConfig}>
                                                <AutoTradeConfig
                                                    type="stop_loss"
                                                    ccy={asset.ccy}
                                                    onSave={(configs) => saveAutoConfig(asset.ccy, 'stop_loss', configs)}
                                                    onClose={() => handleToggle(asset.ccy, 'stop_loss')}
                                                    existingConfigs={asset.auto_config_list.filter(config => config.type === 'stop_loss')}
                                                />
                                            </Box>
                                        </Collapse>
                                        <Collapse
                                            in={expandedRows[asset.ccy]?.limit}
                                            timeout="auto"
                                            unmountOnExit
                                        >
                                            <Box className={classes.limitConfig}>
                                                <AutoTradeConfig
                                                    type="limit"
                                                    ccy={asset.ccy}
                                                    onSave={(configs) => saveAutoConfig(asset.ccy, 'limit', configs)}
                                                    onClose={() => handleToggle(asset.ccy, 'limit')}
                                                    existingConfigs={asset.auto_config_list.filter(config => config.type === 'limit')}
                                                />
                                            </Box>
                                        </Collapse>
                                    </TableCell>
                                </TableRow>
                            </React.Fragment>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Container>
    );
};

export default BalanceList;