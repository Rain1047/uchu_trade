import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Switch,
  Button,
  Drawer,
  Box,
  Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { formatNumber } from '../utils/balanceUtils';
import { AutoTradeConfig } from './AutoTradeConfig';

const useStyles = makeStyles((theme) => ({
  clickableRow: {
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  },
  drawer: {
    width: '700px', // 侧拉框宽度
    padding: theme.spacing(3),
  },
}));

export const BalanceTable = ({ data, onConfigSave, onSwitchToggle }) => {
  const classes = useStyles();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeConfig, setActiveConfig] = useState({ ccy: null });

  const handleEditClick = (ccy) => {
    setActiveConfig({ ccy });
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setActiveConfig({ ccy: null });
  };

  const handleSwitchToggle = (ccy, switchType, currentValue) => {
    const newValue = currentValue === 1 ? 0 : 1; // 切换开关状态
    if (switchType === 'limit_order') {
      onSwitchToggle(ccy, newValue, null); // 更新限价开关
    } else if (switchType === 'stop_loss') {
      onSwitchToggle(ccy, null, newValue); // 更新止损开关
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>币种</TableCell>
            <TableCell align="right">可用余额</TableCell>
            <TableCell align="right">账户权益($)</TableCell>
            <TableCell align="right">持仓均价($)</TableCell>
            <TableCell align="right">总收益率</TableCell>
            <TableCell align="center">限价</TableCell>
            <TableCell align="center">止损</TableCell>
            <TableCell align="center">编辑配置</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => (
            <TableRow key={row.ccy} className={classes.clickableRow}>
              <TableCell>{row.ccy}</TableCell>
              <TableCell align="right">{formatNumber(row.avail_bal)}</TableCell>
              <TableCell align="right">{formatNumber(row.eq_usd)}</TableCell>
              <TableCell align="right">{formatNumber(row.acc_avg_px)}</TableCell>
              <TableCell
                align="right"
                style={{
                  color: parseFloat(row.total_pnl_ratio) >= 0 ? 'green' : 'red',
                }}
              >
                {row.total_pnl_ratio
                  ? `${(parseFloat(row.total_pnl_ratio) * 100).toFixed(2)}%`
                  : '-'}
              </TableCell>
              <TableCell align="center">
                <Switch
                  checked={row.limit_order_switch === 0}
                  onChange={() =>
                    handleSwitchToggle(row.ccy, 'limit_order', row.limit_order_switch)
                  }
                  color="primary"
                />
              </TableCell>
              <TableCell align="center">
                <Switch
                  checked={row.stop_loss_switch === 0}
                  onChange={() =>
                    handleSwitchToggle(row.ccy, 'stop_loss', row.stop_loss_switch)
                  }
                  color="primary"
                />
              </TableCell>
              <TableCell align="center">
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => handleEditClick(row.ccy)}
                >
                  编辑
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 侧拉框 */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={handleDrawerClose}
        classes={{ paper: classes.drawer }}
      >
        <Typography variant="h6" gutterBottom>
          编辑配置 - {activeConfig.ccy}
        </Typography>
        <AutoTradeConfig
          ccy={activeConfig.ccy}
          onSave={(configs) => {
            onConfigSave(configs);
            handleDrawerClose();
          }}
          onClose={handleDrawerClose}
          existingConfigs={
            data.find((item) => item.ccy === activeConfig.ccy)?.auto_config_list || []
          }
        />
      </Drawer>
    </TableContainer>
  );
};
