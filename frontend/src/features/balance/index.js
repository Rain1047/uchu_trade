import React, { useState, useEffect, useCallback } from 'react';
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
    Box,
    Typography,
    Snackbar,
    CircularProgress,
    Dialog,
    Tabs,
    Tab
} from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import { makeStyles, alpha } from '@material-ui/core/styles';
import { debounce } from 'lodash';
import { useBalance } from './hooks/useBalance';
import { AutoTradeConfig } from './components/AutoTradeConfig';
import { PositionTable } from './components/PositionTable';
import { OrderTable } from './components/OrderTable';
import { BalanceHeader } from './components/BalanceHeader';
import { formatNumber, formatBalance, calculatePrice } from './utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        marginTop: theme.spacing(3),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    paper: {
        backgroundColor: alpha(theme.palette.background.paper, 0.1),
        backdropFilter: 'blur(8px)',
        boxShadow: theme.shadows[4],
        width: '95%',
        maxWidth: '2000px',
        margin: '0 auto',
    },
    table: {
        tableLayout: 'fixed',
        '& .MuiTableCell-root': {
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            color: theme.palette.text.primary,
            padding: theme.spacing(1.5),
        },
        '& .MuiTableCell-head': {
            fontWeight: 500,
            whiteSpace: 'nowrap',
        },
    },
    clickableRow: {
        cursor: 'pointer',
        '&:hover': {
            backgroundColor: `${alpha(theme.palette.action.hover, 0.1)} !important`,
        },
    },
    expandedContent: {
        padding: theme.spacing(3),
        backgroundColor: alpha(theme.palette.background.paper, 0.05),
    },
    cellCurrency: {
        width: '10%',
    },
    cellNumber: {
        width: '15%',
    },
    cellAction: {
        width: '12%',
    },
    tabsContainer: {
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        marginBottom: theme.spacing(2),
    },
    loadingContainer: {
        padding: theme.spacing(4),
        textAlign: 'center',
    },
    errorContainer: {
        padding: theme.spacing(4),
        textAlign: 'center',
        color: theme.palette.error.main,
    },
}));

const BalanceList = () => {
    const classes = useStyles();
    const [refreshing, setRefreshing] = useState(false);
    const [localAssets, setLocalAssets] = useState([]);
    const [expandedRow, setExpandedRow] = useState(null);
    const [activeTab, setActiveTab] = useState(0);
    const [configDialog, setConfigDialog] = useState({ open: false, type: null, ccy: null });
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });

    const {
        assets,
        loading,
        error,
        fetchBalance,
        saveAutoConfig
    } = useBalance();

    useEffect(() => {
        if (assets && assets.length > 0) {
            setLocalAssets(assets);
        }
    }, [assets]);

    const showMessage = useCallback((message, severity = 'success') => {
        setSnackbar({
            open: true,
            message,
            severity
        });
    }, []);

    const handleRefresh = async () => {
        setRefreshing(true);
        await fetchBalance();
        setRefreshing(false);
    };

    const handleRowClick = (ccy) => {
        setExpandedRow(expandedRow === ccy ? null : ccy);
        setActiveTab(0);
    };

    const handleSwitchClick = (e, ccy, type) => {
        e.stopPropagation();
        setConfigDialog({ open: true, type, ccy });
    };

    const handleConfigClose = () => {
        setConfigDialog({ open: false, type: null, ccy: null });
    };

    const handleConfigSave = async (configs) => {
        try {
            const success = await saveAutoConfig(
                configDialog.ccy,
                configDialog.type,
                configs
            );
            if (success) {
                showMessage('配置已保存');
                handleConfigClose();
                fetchBalance();
            } else {
                showMessage('保存失败', 'error');
            }
        } catch (error) {
            showMessage('保存失败', 'error');
        }
    };

    useEffect(() => {
        fetchBalance();
    }, [fetchBalance]);

    if (loading && !refreshing) {
        return (
            <Container className={classes.root}>
                <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />
                <Paper className={classes.loadingContainer}>
                    <CircularProgress size={32} />
                </Paper>
            </Container>
        );
    }

    if (error) {
        return (
            <Container className={classes.root}>
                <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />
                <Paper className={classes.errorContainer}>
                    <Typography color="error">{error}</Typography>
                </Paper>
            </Container>
        );
    }

    return (
        <Container className={classes.root}>
            <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />

            <TableContainer component={Paper} className={classes.paper}>
                <Table className={classes.table}>
                    <TableHead>
                        <TableRow>
                            <TableCell className={classes.cellCurrency}>币种</TableCell>
                            <TableCell className={classes.cellNumber} align="right">可用余额</TableCell>
                            <TableCell className={classes.cellNumber} align="right">账户权益</TableCell>
                            <TableCell className={classes.cellNumber} align="right">当前价格</TableCell>
                            <TableCell className={classes.cellNumber} align="right">持仓均价</TableCell>
                            <TableCell className={classes.cellAction} align="center">自动止损</TableCell>
                            <TableCell className={classes.cellAction} align="center">自动限价</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {localAssets.map((asset) => (
                            <React.Fragment key={asset.ccy}>
                                <TableRow
                                    hover
                                    onClick={() => handleRowClick(asset.ccy)}
                                    className={classes.clickableRow}
                                >
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
                                            onChange={(e) => handleSwitchClick(e, asset.ccy, 'stop_loss')}
                                            onClick={(e) => e.stopPropagation()}
                                            color="primary"
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Switch
                                            checked={asset.limit_order_switch === 'true'}
                                            onChange={(e) => handleSwitchClick(e, asset.ccy, 'limit_order')}
                                            onClick={(e) => e.stopPropagation()}
                                            color="primary"
                                        />
                                    </TableCell>
                                </TableRow>
                                {expandedRow === asset.ccy && (
                                    <TableRow>
                                        <TableCell colSpan={7} className={classes.expandedContent}>
                                            <Box className={classes.tabsContainer}>
                                                <Tabs
                                                    value={activeTab}
                                                    onChange={(e, newValue) => setActiveTab(newValue)}
                                                    indicatorColor="primary"
                                                    textColor="primary"
                                                >
                                                    <Tab label="当前持仓" />
                                                    <Tab label="活动委托" />
                                                </Tabs>
                                            </Box>
                                            {activeTab === 0 ? (
                                                <PositionTable ccy={asset.ccy} />
                                            ) : (
                                                <OrderTable ccy={asset.ccy} />
                                            )}
                                        </TableCell>
                                    </TableRow>
                                )}
                            </React.Fragment>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog
                open={configDialog.open}
                onClose={handleConfigClose}
                maxWidth="md"
                fullWidth
            >
                <AutoTradeConfig
                    type={configDialog.type}
                    ccy={configDialog.ccy}
                    existingConfigs={
                        localAssets.find(a => a.ccy === configDialog.ccy)?.auto_config_list || []
                    }
                    onSave={handleConfigSave}
                    onClose={handleConfigClose}
                />
            </Dialog>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={3000}
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