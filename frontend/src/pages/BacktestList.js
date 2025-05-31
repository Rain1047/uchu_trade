import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Grid,
    Paper,
    Typography,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Tooltip,
    Chip,
    Box,
    CircularProgress,
    Snackbar,
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    MenuItem,
    FormControl,
    InputLabel,
    Select
} from '@mui/material';
import {
    Add,
    Delete,
    Refresh,
    PlayArrow,
    Stop,
    Info,
    TrendingUp,
    TrendingDown,
    ShowChart
} from '@mui/icons-material';
import { format } from 'date-fns';
import axios from 'axios';
import { useTheme } from '@mui/material/styles';

const BacktestList = () => {
    const navigate = useNavigate();
    const theme = useTheme();
    
    const [backtests, setBacktests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [snackbarSeverity, setSnackbarSeverity] = useState('info');
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [newBacktest, setNewBacktest] = useState({
        entry_strategy: '',
        exit_strategy: '',
        filter_strategy: '',
        symbols: [],
        timeframe: '1h',
        initial_cash: 10000,
        risk_percent: 1,
        commission: 0.001,
        start_date: '',
        end_date: '',
        description: '',
        tags: []
    });
    
    // 轮询间隔（毫秒）
    const POLLING_INTERVAL = 2000;
    
    useEffect(() => {
        fetchBacktests();
        
        // 设置轮询
        const interval = setInterval(fetchBacktests, POLLING_INTERVAL);
        
        // 清理函数
        return () => clearInterval(interval);
    }, []);
    
    const fetchBacktests = async () => {
        try {
            const response = await axios.get('/api/backtest');
            setBacktests(response.data);
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.detail || '加载回测列表失败');
            setLoading(false);
            showSnackbar('加载回测列表失败', 'error');
        }
    };
    
    const handleCreateBacktest = async () => {
        try {
            const response = await axios.post('/api/backtest', newBacktest);
            showSnackbar('回测已创建', 'success');
            setCreateDialogOpen(false);
            fetchBacktests();
        } catch (err) {
            showSnackbar('创建回测失败', 'error');
        }
    };
    
    const handleCancelBacktest = async (configKey) => {
        try {
            await axios.delete(`/api/backtest/${configKey}`);
            showSnackbar('回测已取消', 'info');
            fetchBacktests();
        } catch (err) {
            showSnackbar('取消回测失败', 'error');
        }
    };
    
    const handleDeleteBacktest = async (configKey) => {
        try {
            await axios.delete(`/api/backtest/${configKey}`);
            showSnackbar('回测已删除', 'info');
            fetchBacktests();
        } catch (err) {
            showSnackbar('删除回测失败', 'error');
        }
    };
    
    const showSnackbar = (message, severity = 'info') => {
        setSnackbarMessage(message);
        setSnackbarSeverity(severity);
        setSnackbarOpen(true);
    };
    
    const handleSnackbarClose = () => {
        setSnackbarOpen(false);
    };
    
    const renderStatus = (status, progress) => {
        let statusColor;
        let statusIcon;
        
        switch (status) {
            case 'running':
                statusColor = 'primary';
                statusIcon = <CircularProgress size={20} />;
                break;
            case 'completed':
                statusColor = 'success';
                statusIcon = <TrendingUp />;
                break;
            case 'failed':
                statusColor = 'error';
                statusIcon = <TrendingDown />;
                break;
            case 'cancelled':
                statusColor = 'warning';
                statusIcon = <Stop />;
                break;
            default:
                statusColor = 'default';
                statusIcon = <Info />;
        }
        
        return (
            <Box display="flex" alignItems="center" gap={1}>
                {statusIcon}
                <Typography color={`${statusColor}.main`}>
                    {status}
                </Typography>
                {status === 'running' && (
                    <Typography variant="body2" color="text.secondary">
                        ({progress}%)
                    </Typography>
                )}
            </Box>
        );
    };
    
    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
                    <CircularProgress />
                </Box>
            </Container>
        );
    }
    
    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* 顶部操作栏 */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    回测列表
                </Typography>
                <Box display="flex" gap={1}>
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={() => setCreateDialogOpen(true)}
                    >
                        新建回测
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<Refresh />}
                        onClick={fetchBacktests}
                    >
                        刷新
                    </Button>
                </Box>
            </Box>
            
            {/* 回测列表 */}
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>配置</TableCell>
                            <TableCell>状态</TableCell>
                            <TableCell>交易对</TableCell>
                            <TableCell>时间框架</TableCell>
                            <TableCell>创建时间</TableCell>
                            <TableCell>操作</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {backtests.map((backtest) => (
                            <TableRow
                                key={backtest.config_key}
                                hover
                                sx={{
                                    '&:hover': {
                                        backgroundColor: theme.palette.mode === 'dark' ? '#363b42' : '#f5f5f5',
                                    }
                                }}
                            >
                                <TableCell>
                                    <Box>
                                        <Typography variant="body1">
                                            {backtest.result?.config?.entry_strategy} / {backtest.result?.config?.exit_strategy}
                                        </Typography>
                                        {backtest.result?.config?.filter_strategy && (
                                            <Typography variant="body2" color="text.secondary">
                                                过滤: {backtest.result.config.filter_strategy}
                                            </Typography>
                                        )}
                                    </Box>
                                </TableCell>
                                <TableCell>
                                    {renderStatus(backtest.status, backtest.progress)}
                                </TableCell>
                                <TableCell>
                                    <Box display="flex" gap={0.5} flexWrap="wrap">
                                        {backtest.result?.config?.symbols.map((symbol) => (
                                            <Chip
                                                key={symbol}
                                                label={symbol}
                                                size="small"
                                                variant="outlined"
                                            />
                                        ))}
                                    </Box>
                                </TableCell>
                                <TableCell>
                                    {backtest.result?.config?.timeframe}
                                </TableCell>
                                <TableCell>
                                    {format(new Date(backtest.result?.created_at || Date.now()), 'yyyy-MM-dd HH:mm:ss')}
                                </TableCell>
                                <TableCell>
                                    <Box display="flex" gap={1}>
                                        <Tooltip title="查看详情">
                                            <IconButton
                                                size="small"
                                                onClick={() => navigate(`/backtest/${backtest.config_key}`)}
                                            >
                                                <ShowChart />
                                            </IconButton>
                                        </Tooltip>
                                        {backtest.status === 'running' && (
                                            <Tooltip title="取消回测">
                                                <IconButton
                                                    size="small"
                                                    color="warning"
                                                    onClick={() => handleCancelBacktest(backtest.config_key)}
                                                >
                                                    <Stop />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                        {backtest.status !== 'running' && (
                                            <Tooltip title="删除回测">
                                                <IconButton
                                                    size="small"
                                                    color="error"
                                                    onClick={() => handleDeleteBacktest(backtest.config_key)}
                                                >
                                                    <Delete />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                    </Box>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            
            {/* 创建回测对话框 */}
            <Dialog
                open={createDialogOpen}
                onClose={() => setCreateDialogOpen(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>新建回测</DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="入场策略"
                                value={newBacktest.entry_strategy}
                                onChange={(e) => setNewBacktest({ ...newBacktest, entry_strategy: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="出场策略"
                                value={newBacktest.exit_strategy}
                                onChange={(e) => setNewBacktest({ ...newBacktest, exit_strategy: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="过滤策略"
                                value={newBacktest.filter_strategy}
                                onChange={(e) => setNewBacktest({ ...newBacktest, filter_strategy: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>时间框架</InputLabel>
                                <Select
                                    value={newBacktest.timeframe}
                                    onChange={(e) => setNewBacktest({ ...newBacktest, timeframe: e.target.value })}
                                    label="时间框架"
                                >
                                    <MenuItem value="1m">1分钟</MenuItem>
                                    <MenuItem value="5m">5分钟</MenuItem>
                                    <MenuItem value="15m">15分钟</MenuItem>
                                    <MenuItem value="30m">30分钟</MenuItem>
                                    <MenuItem value="1h">1小时</MenuItem>
                                    <MenuItem value="4h">4小时</MenuItem>
                                    <MenuItem value="1d">1天</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="交易对（用逗号分隔）"
                                value={newBacktest.symbols.join(',')}
                                onChange={(e) => setNewBacktest({ ...newBacktest, symbols: e.target.value.split(',').map(s => s.trim()) })}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                type="number"
                                label="初始资金"
                                value={newBacktest.initial_cash}
                                onChange={(e) => setNewBacktest({ ...newBacktest, initial_cash: parseFloat(e.target.value) })}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                type="number"
                                label="风险比例"
                                value={newBacktest.risk_percent}
                                onChange={(e) => setNewBacktest({ ...newBacktest, risk_percent: parseFloat(e.target.value) })}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                type="date"
                                label="开始日期"
                                value={newBacktest.start_date}
                                onChange={(e) => setNewBacktest({ ...newBacktest, start_date: e.target.value })}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                type="date"
                                label="结束日期"
                                value={newBacktest.end_date}
                                onChange={(e) => setNewBacktest({ ...newBacktest, end_date: e.target.value })}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                multiline
                                rows={3}
                                label="描述"
                                value={newBacktest.description}
                                onChange={(e) => setNewBacktest({ ...newBacktest, description: e.target.value })}
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateDialogOpen(false)}>取消</Button>
                    <Button onClick={handleCreateBacktest} variant="contained">创建</Button>
                </DialogActions>
            </Dialog>
            
            {/* 提示消息 */}
            <Snackbar
                open={snackbarOpen}
                autoHideDuration={3000}
                onClose={handleSnackbarClose}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert
                    onClose={handleSnackbarClose}
                    severity={snackbarSeverity}
                    sx={{ width: '100%' }}
                >
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default BacktestList; 