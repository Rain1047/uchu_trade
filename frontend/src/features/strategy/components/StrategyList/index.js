import React, {useEffect, useState} from 'react';
import {
  Box,
  Button,
  Container,
  IconButton,
  Paper,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import {
  Edit as EditIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
} from '@material-ui/icons';
import { useStyles } from './styles';
import {useStrategyApi} from "../../hooks/useStrategyApi";

const StrategyList = ({ onAdd, onEdit, onView }) => {
  const classes = useStyles();
  const { listStrategies } = useStrategyApi();
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取策略列表
  const fetchStrategies = async () => {
    setLoading(true);
    try {
      const result = await listStrategies();
      if (result.success && result.data) {
        setStrategies(result.data.items);
      } else {
        setError('获取策略列表失败');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

   // 组件挂载时获取数据
  useEffect(() => {
    fetchStrategies();
  }, []);

  // Mock data - 替换为实际API数据
  const mockStrategies = [
    {
      id: 1,
      tradingPair: 'BTC-USDT',
      isActive: true,
    },
    {
      id: 2,
      tradingPair: 'ETH-USDT',
      isActive: false,
    },
  ];

  const handleStatusChange = (id) => {
    console.log('Toggle status for strategy:', id);
  };

  return (
    <Container className={classes.root}>
      <Box className={classes.header}>
        <Typography variant="h5">策略列表</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onAdd}
        >
          新建策略
        </Button>
      </Box>

      <Paper className={classes.paper}>
        <TableContainer>
          <Table className={classes.table}>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>策略名称</TableCell>
                <TableCell>交易对</TableCell>
                <TableCell>时间窗口</TableCell>
                <TableCell className={classes.statusCell}>状态</TableCell>
                <TableCell className={classes.actionCell}>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {strategies.map((strategy) => (
                <TableRow key={strategy.id} hover>
                  <TableCell>{strategy.id}</TableCell>
                  <TableCell>{strategy.name}</TableCell>
                  <TableCell>{strategy.trade_pair}</TableCell>
                  <TableCell>{strategy.time_frame}</TableCell>
                  <TableCell>
                    <Switch
                      checked={strategy.switch === 1}
                      onChange={() => handleStatusChange(strategy.id)}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => onView(strategy)}
                      className={classes.actionButton}
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => onEdit(strategy)}
                      className={classes.actionButton}
                    >
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default StrategyList;