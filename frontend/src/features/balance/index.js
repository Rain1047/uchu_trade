import React, { useEffect, useState } from 'react';
import { Container, Paper, Snackbar } from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import { makeStyles } from '@material-ui/core/styles';
import { useBalance } from './hooks/useBalance';
import { BalanceTable } from './components/BalanceTable';
import { BalanceHeader } from './components/BalanceHeader';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        marginTop: theme.spacing(3),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    paper: {
        width: '95%',
        maxWidth: '2000px',
        margin: '0 auto',
    }
}));

const BalanceList = () => {
    const classes = useStyles();
    const [refreshing, setRefreshing] = useState(false);
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
    const { balances, loading, error, fetchBalances, toggleAutoConfig, saveTradeConfig } = useBalance();

    useEffect(() => {
        fetchBalances();
    }, [fetchBalances]);

    const handleRefresh = async () => {
        setRefreshing(true);
        await fetchBalances();
        setRefreshing(false);
    };

    const handleSwitchToggle = async (ccy, type) => {
        const currentBalance = balances.find(b => b.ccy === ccy);
        const currentValue = type === 'stop_loss' ?
            currentBalance.stop_loss_switch === 'true' :
            currentBalance.limit_order_switch === 'true';

        const success = await toggleAutoConfig(ccy, type, !currentValue);
        if (success) {
            showMessage(`${type === 'stop_loss' ? '止损' : '限价'}配置已更新`);
        } else {
            showMessage('更新失败', 'error');
        }
    };
    const [configDialog, setConfigDialog] = useState({ open: false, type: null, ccy: null });

    const handleConfigClose = () => {
      setConfigDialog({ open: false, type: null, ccy: null });
    };


    const handleConfigSave = async (configs) => {
        const success = await saveTradeConfig(configDialog.ccy, configDialog.type, configs);
        if (success) {
            showMessage('配置已保存');
            handleConfigClose();
            fetchBalances();
        } else {
            showMessage('保存失败', 'error');
        }
    };

    const showMessage = (message, severity = 'success') => {
        setSnackbar({ open: true, message, severity });
    };

    if (error) {
        return (
            <Container className={classes.root}>
                <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />
                <Alert severity="error">{error}</Alert>
            </Container>
        );
    }

    return (
        <Container className={classes.root}>
            <BalanceHeader onRefresh={handleRefresh} refreshing={refreshing} />
            <Paper className={classes.paper}>
                <BalanceTable
                    data={balances}
                    loading={loading}
                    onSwitchToggle={handleSwitchToggle}
                    onConfigSave={handleConfigSave}
                />
            </Paper>

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