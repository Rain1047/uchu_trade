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
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
} from '@material-ui/core';
import {
  Edit as EditIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@material-ui/icons';
import { useStyles } from './styles';
import {useStrategyApi} from "../../hooks/useStrategyApi";
import { Alert } from '@material-ui/lab';


const StrategyList = ({ onAdd, onEdit, onView }) => {
  const classes = useStyles();
  const { listStrategies, deleteStrategy, toggleStrategyStatus } = useStrategyApi();

  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // 添加刷新函数
  const refreshList = async () => {
    setLoading(true);
    try {
      const result = await listStrategies();
      if (result.success && result.data) {
        setStrategies(result.data.items);
      } else {
        throw new Error(result.message || '获取策略列表失败');
      }
    } catch (err) {
      setError(err.message);
      showSnackbar(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

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

  // 显示提示信息
  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity,
    });
  };

  // 处理删除
  const handleDeleteClick = (strategy) => {
    setSelectedStrategy(strategy);
    setDeleteDialogOpen(true);
  };

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

  const handleDeleteConfirm = async () => {
    try {
      const result = await deleteStrategy(selectedStrategy.id);
      if (result.success) {
        showSnackbar('策略删除成功');
        await refreshList(); // 重新加载列表
      } else {
        throw new Error(result.message || '删除失败');
      }
    } catch (err) {
      showSnackbar(err.message, 'error');
    } finally {
      setDeleteDialogOpen(false);
      setSelectedStrategy(null);
    }
  };

  // 处理状态切换
  const handleStatusChange = async (id, currentStatus) => {
    try {
      const newStatus = !currentStatus;
      const result = await toggleStrategyStatus(id, newStatus);
      if (result.success) {
        showSnackbar(`策略${newStatus ? '启用' : '禁用'}成功`);
        await refreshList();
      } else {
        throw new Error(result.message || '状态更新失败');
      }
    } catch (err) {
      showSnackbar(err.message, 'error');
    }
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
                <TableCell align="center">状态</TableCell>
                <TableCell align="center">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {strategies.map((strategy) => (
                <TableRow key={strategy.id} hover>
                  <TableCell>{strategy.id}</TableCell>
                  <TableCell>{strategy.name}</TableCell>
                  <TableCell>{strategy.trade_pair}</TableCell>
                  <TableCell>{strategy.time_frame}</TableCell>
                  <TableCell align="center">
                    <Switch
                      checked={strategy.switch === 1}
                      onChange={() => handleStatusChange(strategy.id, strategy.switch === 1)}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => onView(strategy)}
                      className={classes.actionButton}
                      title="查看"
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => onEdit(strategy)}
                      className={classes.actionButton}
                      title="编辑"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(strategy)}
                      className={classes.actionButton}
                      title="删除"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* 删除确认对话框 */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>确认删除</DialogTitle>
        <DialogContent>
          <DialogContentText>
            确定要删除策略 "{selectedStrategy?.name}" 吗？此操作不可撤销。
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
            取消
          </Button>
          <Button onClick={handleDeleteConfirm} color="secondary" autoFocus>
            删除
          </Button>
        </DialogActions>
      </Dialog>

      {/* 提示消息 */}
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

export default StrategyList;