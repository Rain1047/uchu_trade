import React from 'react';
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

const StrategyList = ({ onAdd, onEdit, onView }) => {
  const classes = useStyles();

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