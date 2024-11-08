import React, { useState, useEffect } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Select,
  MenuItem,
  Typography,
  Box,
  Grid,
  Container,
  Chip,
  Card,
  CardContent,
  IconButton
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import {
  ArrowForward as ArrowForwardIcon,
  ArrowBack as ArrowBackIcon
} from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
  paginationContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: theme.spacing(2),
    gap: theme.spacing(2)
  },
  buyChip: {
    backgroundColor: '#1b5e20',  // 深绿色
    color: '#fff'
  },
  sellChip: {
    backgroundColor: '#b71c1c',  // 深红色
    color: '#fff'
  },
  pageControl: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1)  // 减小间距使组件更紧凑
    },
  noteField: {
        '& .MuiOutlinedInput-root': {
            '& fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.23)',
            },
            '&:hover fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
            },
            '&.Mui-focused fieldset': {
                borderColor: theme.palette.primary.main,
            }
        },
        '& .MuiInputBase-input': {
            color: theme.palette.text.primary,
        }
    }
}));

function TradeHistoryTable() {
    const classes = useStyles();
    // 修改渲染买卖方向的部分
    const getSideChipStyle = (side) => {
        return side.toLowerCase() === 'buy' ? classes.buyChip : classes.sellChip;
    };

    // 添加 mock 数据定义
    const mockData = {
        items: [
            {
                trade_id: 'MOCK-001',
                inst_id: 'BTC-USDT',
                side: 'buy',
                fill_px: '42000.50',
                fill_sz: '0.1234',
                fee: '-0.000123',
                fill_time: '1699000000000'
            },
            // ... 其他 mock 数据项
        ],
        total_count: 3,
        page_size: 10,
        page_num: 1
    };

    // 添加状态定义
    const [tradeData, setTradeData] = useState({
        items: [],
        total_count: 0,
        page_size: 10,
        page_num: 1
    });

    const [filters, setFilters] = useState({
        pageSize: 10,
        pageNum: 1,
        inst_id: '',
        fill_start_time: '',
        fill_end_time: ''
    });

    // 计算 Amount 的辅助函数
    const calculateAmount = (price, size, fee) => {
        const amount = (parseFloat(price) * parseFloat(size)) + parseFloat(fee);
        return amount.toFixed(2);  // 保留两位小数
    };

    // 添加数据获取函数
    const fetchData = () => {
        const requestData = {
            pageSize: filters.pageSize,
            pageNum: filters.pageNum,
            inst_id: filters.inst_id,
            fill_start_time: filters.fill_start_time,
            fill_end_time: filters.fill_end_time
        };

        fetch('http://127.0.0.1:8000/api/trades/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 如果需要认证，可以添加
                // 'Authorization': 'Bearer your-token'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (!data.data?.items || data.data.items.length === 0) {
                    console.log('No data returned, using mock data');
                    setTradeData(mockData);
                } else {
                    setTradeData({
                        items: data.data?.items || [],
                        total_count: data.data?.total_count || 0,
                        page_size: data.data?.page_size || 10,
                        page_num: data.data?.page_num || 1
                    });
                }
            } else {
                console.log('API request failed, using mock data');
                setTradeData(mockData);
            }
        })
        .catch(error => {
            console.error('Error fetching trades:', error);
            console.log('Error occurred, using mock data');
            setTradeData(mockData);
        });
    };

    // 添加 useEffect
    useEffect(() => {
        fetchData();
        const intervalId = setInterval(fetchData, 5000);
        return () => clearInterval(intervalId);
    }, [filters]);

    // 添加处理函数
    const handlePageChange = (newPage) => {
        setFilters(prev => ({
            ...prev,
            pageNum: newPage
        }));
    };

    // 在 TradeHistoryTable 组件内添加 notes 状态
    const [notes, setNotes] = useState({});  // 用于存储每个交易的笔记

    // 添加处理笔记更新的函数
    const handleNoteChange = (tradeId, value) => {
        setNotes(prev => ({
            ...prev,
            [tradeId]: value
        }));
    };

    const handleRowsPerPageChange = (event) => {
        setFilters(prev => ({
            ...prev,
            pageSize: parseInt(event.target.value, 10),
            pageNum: 1
        }));
    };

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // 添加时间戳格式化函数
    const formatTimestamp = (timestamp) => {
        try {
            const date = new Date(parseInt(timestamp));
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
        } catch (error) {
            return timestamp;
        }
    };

    return (
        <Container>
            <Typography variant="h5">
                Trade History
                {tradeData === mockData && (
                    <Typography variant="caption">
                        (Using Mock Data)
                    </Typography>
                )}
            </Typography>

            <Card>
                <CardContent>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                variant="outlined"
                                name="inst_id"
                                label="Instrument ID"
                                value={filters.inst_id}
                                onChange={handleFilterChange}
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                variant="outlined"
                                type="datetime-local"
                                name="fill_start_time"
                                label="Start Time"
                                value={filters.fill_start_time}
                                onChange={handleFilterChange}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                variant="outlined"
                                type="datetime-local"
                                name="fill_end_time"
                                label="End Time"
                                value={filters.fill_end_time}
                                onChange={handleFilterChange}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            <Paper>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Trade ID</TableCell>
                                <TableCell>Instrument</TableCell>
                                <TableCell>Side</TableCell>
                                <TableCell>Price</TableCell>
                                {/*<TableCell>Size</TableCell>*/}
                                <TableCell>Amount</TableCell>
                                <TableCell>Time</TableCell>
                                <TableCell>Note</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                        {(tradeData.items || []).map((row) => (
                            <TableRow key={row.trade_id} hover>
                                <TableCell>{row.trade_id}</TableCell>
                                <TableCell>{row.inst_id}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={row.side?.toUpperCase()}
                                        size="small"
                                        className={getSideChipStyle(row.side)}
                                    />
                                </TableCell>
                                <TableCell>{row.fill_px}</TableCell>
                                <TableCell>
                                    {calculateAmount(row.fill_px, row.fill_sz, row.fee)}
                                </TableCell>
                                <TableCell>{formatTimestamp(row.fill_time)}</TableCell>
                                <TableCell>
                                    <TextField
                                        size="small"
                                        variant="outlined"
                                        value={notes[row.trade_id] || ''}
                                        onChange={(e) => handleNoteChange(row.trade_id, e.target.value)}
                                        placeholder="Add note..."
                                        multiline
                                        maxRows={4}
                                        fullWidth
                                        style={{ minWidth: '200px' }}
                                    />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                    </Table>
                </TableContainer>

                <Box className={classes.paginationContainer}>
                    <Select
                        value={filters.pageSize}
                        onChange={handleRowsPerPageChange}
                        variant="outlined"
                    >
                        <MenuItem value={5}>5 per page</MenuItem>
                        <MenuItem value={10}>10 per page</MenuItem>
                        <MenuItem value={20}>20 per page</MenuItem>
                        <MenuItem value={50}>50 per page</MenuItem>
                    </Select>

                    <Box display="flex" alignItems="center" className={classes.pageControl}>
                        <IconButton
                            onClick={() => handlePageChange(filters.pageNum - 1)}
                            disabled={filters.pageNum === 1}
                        >
                            <ArrowBackIcon />
                        </IconButton>
                        <Typography variant="body2" style={{ margin: '0 16px', color: '#fff' }}>
                            Page {filters.pageNum} of {Math.ceil(tradeData.total_count / filters.pageSize)}
                        </Typography>
                        <IconButton
                            size="small"
                            onClick={() => handlePageChange(filters.pageNum + 1)}
                            disabled={filters.pageNum >= Math.ceil(tradeData.total_count / filters.pageSize)}
                        >
                            <ArrowForwardIcon />
                        </IconButton>
                    </Box>
                </Box>
            </Paper>
        </Container>
    );
}

export default TradeHistoryTable;