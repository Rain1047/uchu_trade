import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Switch,
  Typography,
  Button,
} from '@material-ui/core';
import {
  Edit as EditIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
} from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import UpdateStrategy from './UpdateStrategy';

const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(3),
  },
  paper: {
    width: '100%',
    marginBottom: theme.spacing(2),
  },
  table: {
    minWidth: 750,
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing(3),
  },
  actionButton: {
    marginLeft: theme.spacing(1),
  },
  statusCell: {
    width: 120,
  },
  actionCell: {
    width: 120,
  }
}));

const StrategyList = () => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [viewMode, setViewMode] = useState(false);

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
    {
      id: 3,
      tradingPair: 'BNB-USDT',
      isActive: true,
    },
  ];

  const handleStatusChange = (id) => {
    // 处理策略启用/禁用
    // 这里需要调用后端API
    console.log('Toggle status for strategy:', id);
  };

  const handleEdit = (strategy) => {
    setSelectedStrategy(strategy);
    setViewMode(false);
    setOpen(true);
  };

  const handleView = (strategy) => {
    setSelectedStrategy(strategy);
    setViewMode(true);
    setOpen(true);
  };

  const handleAdd = () => {
    setSelectedStrategy(null);
    setViewMode(false);
    setOpen(true);
  };

  return (
    <Container className={classes.root}>
      <Box className={classes.header}>
        <Typography variant="h5">
          策略列表
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAdd}
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
                <TableCell>交易对</TableCell>
                <TableCell className={classes.statusCell}>状态</TableCell>
                <TableCell className={classes.actionCell}>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockStrategies.map((strategy) => (
                <TableRow key={strategy.id} hover>
                  <TableCell>{strategy.id}</TableCell>
                  <TableCell>{strategy.tradingPair}</TableCell>
                  <TableCell>
                    <Switch
                      checked={strategy.isActive}
                      onChange={() => handleStatusChange(strategy.id)}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleView(strategy)}
                      className={classes.actionButton}
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleEdit(strategy)}
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

      <UpdateStrategy
        open={open}
        onClose={() => setOpen(false)}
        strategy={selectedStrategy}
        viewMode={viewMode}
      />
    </Container>
  );
};

export default StrategyList;