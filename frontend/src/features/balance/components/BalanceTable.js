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
  Dialog,
  Box,
  Typography,
  Tab,
  Tabs,
  IconButton
} from '@material-ui/core';
import { KeyboardArrowDown, KeyboardArrowUp } from '@material-ui/icons';
import { AutoTradeConfig } from './AutoTradeConfig';
import { OrderList } from './OrderList';
import { makeStyles } from '@material-ui/core/styles';
import { formatNumber, formatPrice } from '../utils/balanceUtils';

const useStyles = makeStyles((theme) => ({
  clickableRow: {
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  },
  expandedCell: {
    padding: 0,
    backgroundColor: theme.palette.background.default,
  },
  expandedContent: {
    padding: theme.spacing(3),
  },
  profit: {
    color: theme.palette.success.main,
  },
  loss: {
    color: theme.palette.error.main,
  },
}));

export const BalanceTable = ({ data, onConfigSave, onSwitchToggle }) => {
  const classes = useStyles();
  const [expandedRow, setExpandedRow] = useState(null);
  const [configDialog, setConfigDialog] = useState({ open: false, type: null, ccy: null });
  const [activeTab, setActiveTab] = useState(0);

  const handleRowClick = (ccy) => {
    setExpandedRow(expandedRow === ccy ? null : ccy);
  };

  const handleSwitchClick = (e, ccy, type) => {
    e.stopPropagation();
    setConfigDialog({ open: true, type, ccy });
  };

  const handleConfigClose = () => {
    setConfigDialog({ open: false, type: null, ccy: null });
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell>币种</TableCell>
            <TableCell align="right">可用余额</TableCell>
            <TableCell align="right">账户权益($)</TableCell>
            <TableCell align="right">持仓均价($)</TableCell>
            <TableCell align="right">总收益率</TableCell>
            <TableCell align="center">自动止损</TableCell>
            <TableCell align="center">自动限价</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => (
            <React.Fragment key={row.ccy}>
              <TableRow
                hover
                onClick={() => handleRowClick(row.ccy)}
                className={classes.clickableRow}
              >
                <TableCell>
                  <IconButton size="small">
                    {expandedRow === row.ccy ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                  </IconButton>
                </TableCell>
                <TableCell>{row.ccy}</TableCell>
                <TableCell align="right">{formatNumber(row.avail_bal)}</TableCell>
                <TableCell align="right">{formatNumber(row.eq_usd)}</TableCell>
                <TableCell align="right">{formatNumber(row.acc_avg_px)}</TableCell>
                <TableCell align="right" className={parseFloat(row.total_pnl_ratio) >= 0 ? classes.profit : classes.loss}>
                  {row.total_pnl_ratio ? `${(parseFloat(row.total_pnl_ratio) * 100).toFixed(2)}%` : '-'}
                </TableCell>
                <TableCell align="center">
                  <Switch
                    checked={row.stop_loss_switch === 'true'}
                    onChange={(e) => handleSwitchClick(e, row.ccy, 'stop_loss')}
                    color="primary"
                  />
                </TableCell>
                <TableCell align="center">
                  <Switch
                    checked={row.limit_order_switch === 'true'}
                    onChange={(e) => handleSwitchClick(e, row.ccy, 'limit_order')}
                    color="primary"
                  />
                </TableCell>
              </TableRow>
              {expandedRow === row.ccy && (
                <TableRow>
                  <TableCell className={classes.expandedCell} colSpan={8}>
                    <Box className={classes.expandedContent}>
                      <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        indicatorColor="primary"
                        textColor="primary"
                        variant="fullWidth"
                      >
                        <Tab label="生效中委托" />
                        <Tab label="已成交委托" />
                      </Tabs>
                      <Box mt={2}>
                        {activeTab === 0 ? (
                          <OrderList orders={row.live_spot_algo_order_records} />
                        ) : (
                          <OrderList orders={row.filled_spot_algo_order_records} />
                        )}
                      </Box>
                    </Box>
                  </TableCell>
                </TableRow>
              )}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>

      <Dialog
        open={configDialog.open}
        onClose={handleConfigClose}
        maxWidth="sm"
        fullWidth
      >
        <AutoTradeConfig
          type={configDialog.type}
          ccy={configDialog.ccy}
          onSave={onConfigSave}
          onClose={handleConfigClose}
          existingConfigs={data.find(item => item.ccy === configDialog.ccy)?.auto_config_list || []}
        />
      </Dialog>
    </TableContainer>
  );
};