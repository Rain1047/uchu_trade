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
    CircularProgress, Tooltip, IconButton
} from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import { makeStyles, alpha } from '@material-ui/core/styles';
import { debounce } from 'lodash';
import { useBalance } from './hooks/useBalance';
import TradeConfigForm from './components/TradeConfigForm';
import { BalanceHeader } from './components/BalanceHeader';
import { TABLE_COLUMNS } from './constants/balanceConstants';
import { calculatePrice, formatNumber, formatBalance } from './utils/balanceUtils';
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        marginTop: theme.spacing(3),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center', // 居中对齐
    },
    paper: {
        backgroundColor: alpha(theme.palette.background.paper, 0.1),
        backdropFilter: 'blur(8px)',
        boxShadow: theme.shadows[4],
        width: '95%', // 使用百分比而不是固定宽度
        maxWidth: '2000px', // 设置最大宽度避免在超大屏幕上过宽
        margin: '0 auto', // 居中
    },
    table: {
        tableLayout: 'fixed', // 使用固定表格布局提高性能
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
    tableContainer: {
        overflowX: 'auto',
        '&::-webkit-scrollbar': {
            display: 'none',
        },
        scrollbarWidth: 'none',
        '-ms-overflow-style': 'none',
    },
    configsContainer: {
        display: 'flex',
        flexDirection: 'row',
        gap: theme.spacing(2),
        padding: theme.spacing(2),
        backgroundColor: alpha(theme.palette.background.paper, 0.03),
        width: '100%',
    },
    configSection: {
        flex: '1 1 0', // 使用flex grow和shrink确保平均分配空间
        minWidth: '300px', // 设置最小宽度避免内容过于拥挤
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing(1),
        padding: theme.spacing(2),
        borderRadius: theme.shape.borderRadius,
        backgroundColor: alpha(theme.palette.background.paper, 0.05),
        marginRight: theme.spacing(2),
        '&:last-child': {
            marginRight: 0,
        },
    },
    expandIconCell: {
        width: '48px',
        padding: '0.8px',
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    },
    expandIcon: {
        padding: 4,
        color: theme.palette.text.secondary,
        '&:hover': {
            color: theme.palette.primary.main,
        }
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
    },
    // 为不同类型的单元格设置合适的宽度比例
    cellExpand: {
        width: '48px',
        padding: '0 8px',
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
    expandedRow: {
        backgroundColor: 'transparent !important',
    },
}));

const BalanceList = () => {
    const classes = useStyles();
    const [refreshing, setRefreshing] = useState(false);
    const [localAssets, setLocalAssets] = useState([]);
    const [expandedRows, setExpandedRows] = useState(new Set());
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });

    const [pendingToggles, setPendingToggles] = useState(new Set());

    const {
        assets,
        loading,
        error,
        fetchBalance,
        saveAutoConfig,
        toggleAutoSwitch
    } = useBalance();

    // 同步 assets 到 localAssets
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

    const handleSwitchChange = useCallback((ccy, type) => {
        setLocalAssets(prev => prev.map(asset => {
            if (asset.ccy === ccy) {
                const newValue = type === 'stop_loss'
                    ? asset.stop_loss_switch !== 'true'
                    : asset.limit_order_switch !== 'true';

                // Expand the row to show config form
                setExpandedRows(prev => {
                    const newSet = new Set(prev);
                    newSet.add(ccy);
                    return newSet;
                });

                // Add to pending toggles
                setPendingToggles(prev => {
                    const newSet = new Set(prev);
                    newSet.add(`${ccy}-${type}`);
                    return newSet;
                });

                return {
                    ...asset,
                    [type === 'stop_loss' ? 'stop_loss_switch' : 'limit_order_switch']:
                        newValue ? 'true' : 'false'
                };
            }
            return asset;
        }));
    }, []);

    const handleConfigSave = async (ccy, type, configs) => {
        try {
            // Here you can call your API to save configs
            // await saveAutoConfig(ccy, type, configs);

            // Remove from pending toggles
            setPendingToggles(prev => {
                const newSet = new Set(prev);
                newSet.delete(`${ccy}-${type}`);
                return newSet;
            });

            showMessage('配置已保存');
        } catch (error) {
            showMessage('保存失败', 'error');
        }
    };

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
                            <TableCell className={classes.cellExpand} />
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
                                <TableRow hover>
                                    <TableCell className={classes.expandIconCell}>
                                        <Tooltip title={expandedRows.has(asset.ccy) ? "收起" : "展开"}>
                                            <IconButton
                                                size="small"
                                                className={classes.expandIcon}
                                                onClick={() => {
                                                    setExpandedRows(prev => {
                                                        const newSet = new Set(prev);
                                                        if (newSet.has(asset.ccy)) {
                                                            newSet.delete(asset.ccy);
                                                        } else {
                                                            newSet.add(asset.ccy);
                                                        }
                                                        return newSet;
                                                    });
                                                }}
                                            >
                                                {expandedRows.has(asset.ccy) ?
                                                    <KeyboardArrowUpIcon fontSize="small" /> :
                                                    <KeyboardArrowDownIcon fontSize="small" />
                                                }
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
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
                                            onChange={() => handleSwitchChange(asset.ccy, 'stop_loss')}
                                            color="primary"
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Switch
                                            checked={asset.limit_order_switch === 'true'}
                                            onChange={() => handleSwitchChange(asset.ccy, 'limit')}
                                            color="primary"
                                        />
                                    </TableCell>
                                </TableRow>
                                {expandedRows.has(asset.ccy) && (
                                    <TableRow>
                                        <TableCell colSpan={7} style={{ padding: 0 }}>
                                            <Box className={classes.configsContainer}>
                                                {asset.stop_loss_switch === 'true' && (
                                                    <Box className={classes.configSection}>
                                                        <Typography className={classes.configTitle}>
                                                            自动止损配置
                                                        </Typography>
                                                        <TradeConfigForm
                                                            configs={asset.auto_config_list?.filter(
                                                                config => config.type === 'stop_loss'
                                                            ) || []}
                                                            onChange={(configs) => handleConfigSave(
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
                                                            configs={asset.auto_config_list?.filter(
                                                                config => config.type === 'limit'
                                                            ) || []}
                                                            onChange={(configs) => handleConfigSave(
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