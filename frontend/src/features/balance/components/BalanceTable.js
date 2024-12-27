import React, { useState } from 'react';
import axios from 'axios';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Drawer,
  Box,
  Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Switch from '@mui/material/Switch';
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
    width: '1400px', // 设置固定宽度
  },
  drawerPaper: {
    width: '1400px', // 设置 Drawer 的宽度
  },
}));

export const BalanceTable = ({ data, onConfigSave, onSwitchToggle }) => {
  const classes = useStyles();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeConfig, setActiveConfig] = useState({ ccy: null });
  const [configData, setConfigData] = useState([]); // 存储当前配置数据
  const [isStopLoss, setIsStopLoss] = useState(true); // true 为止损，false 为限价

  const handleEditClick = (ccy) => {
    const configType = isStopLoss ? 'stop_loss' : 'limit_order';
    setActiveConfig({ ccy, config_type: configType });
    fetchConfigData(ccy, configType);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setActiveConfig({ ccy: null });
  };

  const handleSwitchChange = () => {
    const newConfigType = !isStopLoss ? 'stop_loss' : 'limit_order';
    setIsStopLoss((prev) => !prev);
    if (activeConfig.ccy) {
      fetchConfigData(activeConfig.ccy, newConfigType); // 切换时重新加载数据
    }
  };

  const handleSwitchToggle = (ccy, switchType, currentValue) => {
    const newValue = currentValue === 1 ? 0 : 1; // 切换开关状态
    if (switchType === 'limit_order') {
      onSwitchToggle(ccy, newValue, null); // 更新限价开关
    } else if (switchType === 'stop_loss') {
      onSwitchToggle(ccy, null, newValue); // 更新止损开关
    }
  };

  const handleSave = (updatedConfigs) => {
    console.log('保存的配置:', updatedConfigs);
    setDrawerOpen(false);
  };

  const fetchConfigData = async (ccy, configType) => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/balance/list_balance_configs', {
        params: { ccy, config_type: configType },
      });
      setConfigData(response.data.data || []); // 假设后端返回的配置数据在 data.data 中
      setDrawerOpen(true);
    } catch (error) {
      console.error('获取配置数据失败:', error);
      alert('无法加载配置数据，请稍后重试。');
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
            <TableCell align="center">查看&编辑配置</TableCell>
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
                  查看&编辑
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 侧拉框 */}
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box width="1400px" p={3}>
          <Typography variant="h6">
            {activeConfig.config_type === 'stop_loss' ? '止损配置' : '限价配置'} - {activeConfig.ccy}
          </Typography>
          {configData.length > 0 ? (
            <AutoTradeConfig
              ccy={activeConfig.ccy}
              onSave={handleSave}
              onClose={() => setDrawerOpen(false)}
              existingConfigs={configData}
            />
          ) : (
            <Typography color="textSecondary">当前无配置</Typography>
          )}
        </Box>
      </Drawer>
    </TableContainer>
  );
};
