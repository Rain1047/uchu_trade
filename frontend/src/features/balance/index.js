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
    CircularProgress
} from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import { makeStyles, alpha } from '@material-ui/core/styles';
import { debounce } from 'lodash';
import { useBalance } from './hooks/useBalance';
import TradeConfigForm from './components/TradeConfigForm';
import { BalanceHeader } from './components/BalanceHeader';
import { TABLE_COLUMNS } from './constants/balanceConstants';
import { calculatePrice, formatNumber, formatBalance } from './utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        marginTop: theme.spacing(3),
    },
    paper: {
        backgroundColor: alpha(theme.palette.background.paper, 0.1),
        backdropFilter: 'blur(8px)',
        boxShadow: theme.shadows[4],
    },
    table: {
        '& .MuiTableCell-root': {
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            color: theme.palette.text.primary,
        },
        '& .MuiTableHead-root .MuiTableCell-root': {
            backgroundColor: alpha(theme.palette.background.paper, 0.05),
            color: theme.palette.text.secondary,
            fontWeight: 500,
        },
        '& .MuiTableBody-root .MuiTableRow-root': {
            '&:hover': {
                backgroundColor: alpha(theme.palette.action.hover, 0.1),
            },
            '&:nth-of-type(odd)': {
                backgroundColor: alpha(theme.palette.background.paper, 0.03),
            },
        },
    },
    configsContainer: {
        display: 'flex',
        flexDirection: 'row',
        gap: theme.spacing(2),
        padding: theme.spacing(2),
        backgroundColor: alpha(theme.palette.background.paper, 0.03),
    },
    configSection: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing(1),
        padding: theme.spacing(2),
        borderRadius: theme.shape.borderRadius,
        backgroundColor: alpha(theme.palette.background.paper, 0.05),
    },
    configTitle: {
        fontSize: '0.875rem',
        color: theme.palette.text.secondary,
        marginBottom: theme.spacing(1),
    },
    switchBase: {
        color: theme.palette.grey[500],
        '&$checked': {
            color: theme.palette.primary.main,
        },
        '&$checked + $track': {
            backgroundColor: theme.palette.primary.main,
        },
        transition: theme.transitions.create(['transform', 'color'], {
            duration: theme.transitions.duration.shortest,
        }),
    },
    checked: {},
    track: {
        opacity: 0.3,
    },
    loadingContainer: {
        padding: theme.spacing(4),
        textAlign: 'center',
    },
    errorContainer: {
        padding: theme.spacing(4),
        textAlign: 'center',
        color: theme.palette.error.main,
    }
}));

const BalanceList = () => {
    const classes = useStyles();
    const [refreshing, setRefreshing] = useState(false);
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
        saveAutoConfig,
        toggleAutoSwitch
    } = useBalance();

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

    const handleSwitchChange = useCallback(async (ccy, type, currentValue) => {
        const success = await toggleAutoSwitch(ccy, type, !currentValue);
        if (success) {
            showMessage(`${type === 'stop_loss' ? '自动止损' : '自动限价'}已${!currentValue ? '开启' : '关闭'}`);
        } else {
            showMessage('操作失败', 'error');
        }
    }, [toggleAutoSwitch, showMessage]);

    const debouncedSave = useCallback(
        debounce(async (ccy, type, configs) => {
            const success = await saveAutoConfig(ccy, type, configs);
            showMessage(success ? '配置已保存' : '保存失败', success ? 'success' : 'error');
        }, 500),
        [saveAutoConfig, showMessage]
    );

    const handleConfigChange = useCallback((ccy, type, configs) => {
        debouncedSave(ccy, type, configs);
    }, [debouncedSave]);

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
                                            onChange={() => handleSwitchChange(
                                                asset.ccy,
                                                'stop_loss',
                                                asset.stop_loss_switch === 'true'
                                            )}
                                            color="primary"
                                            classes={{
                                                switchBase: classes.switchBase,
                                                checked: classes.checked,
                                                track: classes.track
                                            }}
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Switch
                                            checked={asset.limit_order_switch === 'true'}
                                            onChange={() => handleSwitchChange(
                                                asset.ccy,
                                                'limit',
                                                asset.limit_order_switch === 'true'
                                            )}
                                            color="primary"
                                            classes={{
                                                switchBase: classes.switchBase,
                                                checked: classes.checked,
                                                track: classes.track
                                            }}
                                        />
                                    </TableCell>
                                </TableRow>
                                {(asset.stop_loss_switch === 'true' || asset.limit_order_switch === 'true') && (
                                    <TableRow>
                                        <TableCell colSpan={7} style={{ padding: 0 }}>
                                            <Box className={classes.configsContainer}>
                                                {asset.stop_loss_switch === 'true' && (
                                                    <Box className={classes.configSection}>
                                                        <Typography className={classes.configTitle}>
                                                            自动止损配置
                                                        </Typography>
                                                        <TradeConfigForm
                                                            configs={asset.auto_config_list.filter(
                                                                config => config.type === 'stop_loss'
                                                            )}
                                                            onChange={configs => handleConfigChange(
                                                                asset.ccy,
                                                                'stop_loss',
                                                                configs
                                                            )}
                                                        />
                                                    </Box>
                                                )}
                                                {asset.limit_order_switch === 'true' && (
                                                    <Box className={classes.configSection}>
                                                        <Typography className={classes.configTitle}>
                                                            自动限价配置
                                                        </Typography>
                                                        <TradeConfigForm
                                                            configs={asset.auto_config_list.filter(
                                                                config => config.type === 'limit'
                                                            )}
                                                            onChange={configs => handleConfigChange(
                                                                asset.ccy,
                                                                'limit',
                                                                configs
                                                            )}
                                                        />
                                                    </Box>
                                                )}
                                            </Box>
                                        </TableCell>
                                    </TableRow>
                                )}
                            </React.Fragment>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

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