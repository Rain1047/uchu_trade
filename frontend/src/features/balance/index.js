import React, { useState, useEffect } from 'react';
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
    CircularProgress,
    Typography,
    Snackbar
} from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import { Refresh as RefreshIcon } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import { green, blue } from '@material-ui/core/colors';
import AutoTradeConfig from './components/AutoTradeConfig';
import { useBalance } from './hooks/useBalance';
import { TABLE_COLUMNS } from './constants/balanceConstants';
import { calculatePrice, formatNumber, formatBalance } from './utils/balanceUtils';
import { BalanceHeader } from './components/BalanceHeader';

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
    }
}));

const BalanceList = () => {
    const classes = useStyles();
    const [expandedRows, setExpandedRows] = useState({});
    const [refreshing, setRefreshing] = useState(false);
    const { assets, loading, error, fetchBalance, saveAutoConfig } = useBalance();
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            await fetchBalance();
        } finally {
            setRefreshing(false);
        }
    };

    const handleToggle = (ccy, type) => {
        setExpandedRows(prev => ({
            ...prev,
            [ccy]: {
                ...prev[ccy],
                [type]: !prev[ccy]?.[type]
            }
        }));
    };

    // 首次加载时获取数据
    useEffect(() => {
        fetchBalance();
    }, [fetchBalance]);

    if (loading && !refreshing) {
        return (
            <Container className={classes.root}>
                <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />
                <Paper className={classes.loading}>
                    <Typography>Loading...</Typography>
                </Paper>
            </Container>
        );
    }

    if (error) {
        return (
            <Container className={classes.root}>
                <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />
                <Paper className={classes.error}>
                    <Typography>Error: {error}</Typography>
                </Paper>
            </Container>
        );
    }

    return (
        <Container className={classes.root}>
            <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />

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

            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
            >
                <Alert
                    onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
                    severity={snackbar.severity}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default BalanceList;