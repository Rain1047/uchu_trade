// components/BalanceTable.js
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
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { AutoTradeConfig } from './AutoTradeConfig';
import { formatNumber, formatPercentage } from '../utils/balanceUtils';

// 自定义绿色按钮
const GreenButton = styled(Button)({
  color: '#2EE5AC',
  borderColor: '#2EE5AC',
  '&:hover': {
    backgroundColor: 'rgba(46, 229, 172, 0.08)',
    borderColor: '#2EE5AC',
  },
});

// 自定义绿色开关
const GreenSwitch = styled(Switch)({
  '& .MuiSwitch-switchBase.Mui-checked': {
    color: '#2EE5AC',
    '&:hover': {
      backgroundColor: 'rgba(46, 229, 172, 0.08)',
    },
  },
  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
    backgroundColor: '#2EE5AC',
  },
});

// 自定义暗色主题的 TableCell
const StyledTableCell = styled(TableCell)(({ theme }) => ({
  color: '#ffffff',
  borderBottom: 'none',
  padding: '16px',
  '&.MuiTableCell-head': {
    backgroundColor: '#1A1A1A',
    color: '#999',
    fontWeight: 400,
  },
}));

// 自定义表格行样式
const StyledTableRow = styled(TableRow)(({ theme }) => ({
  // 奇数行和偶数行使用不同的背景色
  '&:nth-of-type(odd)': {
    backgroundColor: '#1A1A1A',
  },
  '&:nth-of-type(even)': {
    backgroundColor: '#121212',
  },
  // hover 效果
  '&:hover': {
    backgroundColor: '#242424 !important', // 使用 !important 确保 hover 效果优先
    cursor: 'pointer',
  },
  // 去掉最后一个单元格的底部边框
  '&:last-child td, &:last-child th': {
    borderBottom: 0,
  },
}));

// 自定义暗色主题的 TableContainer
const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  backgroundColor: theme.palette.grey[900],
  '& .MuiPaper-root': {
    backgroundColor: 'transparent',
    boxShadow: 'none',
  }
}));

export const BalanceTable = ({ data, onSwitchToggle, onConfigSave }) => {
  const [configDrawer, setConfigDrawer] = useState({
    open: false,
    ccy: null,
    type: null
  });

  const handleConfigOpen = (ccy, type) => {
    setConfigDrawer({
      open: true,
      ccy,
      type: 'limit_order'
    });
  };

  const handleDrawerClose = () => {
    setConfigDrawer({
      open: false,
      ccy: null,
      type: 'limit_order'
    });
  };

  return (
    <>
      <StyledTableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <StyledTableCell>币种</StyledTableCell>
              <StyledTableCell align="right">可用余额</StyledTableCell>
              <StyledTableCell align="right">账户权益($)</StyledTableCell>
              <StyledTableCell align="right">持仓均价($)</StyledTableCell>
              <StyledTableCell align="right">总收益率</StyledTableCell>
              <StyledTableCell align="center">限价</StyledTableCell>
              <StyledTableCell align="center">止损</StyledTableCell>
              <StyledTableCell align="center">编辑配置</StyledTableCell>
              <StyledTableCell align="center">执行记录</StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <StyledTableRow key={row.ccy}>
                <StyledTableCell>{row.ccy}</StyledTableCell>
                <StyledTableCell align="right">{formatNumber(row.avail_eq)}</StyledTableCell>
                <StyledTableCell align="right">{formatNumber(row.eq_usd)}</StyledTableCell>
                <StyledTableCell align="right">{formatNumber(row.acc_avg_px)}</StyledTableCell>
                <StyledTableCell
                  align="right"
                  sx={{
                    color: (theme) =>
                      parseFloat(row.total_pnl_ratio) >= 0
                        ? theme.palette.success.main
                        : theme.palette.error.main
                  }}
                >
                  {formatPercentage(row.total_pnl_ratio)}
                </StyledTableCell>
                <StyledTableCell align="center">
                  <GreenSwitch
                    checked={row.limit_order_switch === 'true'}
                    onChange={() => onSwitchToggle(row.ccy, 'limit_order')}
                  />
                </StyledTableCell>
                <StyledTableCell align="center">
                  <GreenSwitch
                    checked={row.stop_loss_switch === 'true'}
                    onChange={() => onSwitchToggle(row.ccy, 'stop_loss')}
                  />
                </StyledTableCell>
                <StyledTableCell align="center">
                  <GreenButton
                    variant="outlined"
                    size="small"
                    onClick={() => handleConfigOpen(row.ccy)}
                  >
                    编辑配置
                  </GreenButton>
                </StyledTableCell>

                <StyledTableCell align="center">
                  <GreenButton
                    variant="outlined"
                    size="small"
                    onClick={() => handleConfigOpen(row.ccy)}
                  >
                    执行记录
                  </GreenButton>
                </StyledTableCell>
              </StyledTableRow>
            ))}
          </TableBody>
        </Table>
      </StyledTableContainer>

      <Drawer
        anchor="right"
        open={configDrawer.open}
        onClose={handleDrawerClose}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: '80%', md: '1000px' },
            maxWidth: '1200px',
            bgcolor: 'grey.900',
          }
        }}
      >
        {configDrawer.open && (
          <AutoTradeConfig
            ccy={configDrawer.ccy}
            initialType={configDrawer.type}
            onClose={handleDrawerClose}
            onSave={onConfigSave}
          />
        )}
      </Drawer>
    </>
  );
};