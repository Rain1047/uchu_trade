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
  Dialog,
  Box,
  Typography,
  Tab,
  Tabs,
} from '@material-ui/core';
import { KeyboardArrowDown, KeyboardArrowUp } from 'lucide-react';
import { AutoTradeConfig } from './AutoTradeConfig';
import { PositionTable } from './PositionTable';
import { OrderTable } from './OrderTable';
import { useBalanceTableStyles } from '../utils/styles';

export const BalanceTable = ({ data, onConfigSave, onSwitchToggle }) => {
  const classes = useBalanceTableStyles();
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
            <TableCell align="right">美元价值</TableCell>
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
                  {expandedRow === row.ccy ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                </TableCell>
                <TableCell>{row.ccy}</TableCell>
                <TableCell align="right">{row.availBal}</TableCell>
                <TableCell align="right">{row.eqUsd}</TableCell>
                <TableCell align="center">
                  <Switch
                    checked={row.stopLossEnabled}
                    onChange={(e) => handleSwitchClick(e, row.ccy, 'stop_loss')}
                    color="primary"
                  />
                </TableCell>
                <TableCell align="center">
                  <Switch
                    checked={row.limitOrderEnabled}
                    onChange={(e) => handleSwitchClick(e, row.ccy, 'limit_order')}
                    color="primary"
                  />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className={classes.expandedCell} colSpan={6}>
                  {expandedRow === row.ccy && (
                    <Box className={classes.expandedContent}>
                      <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        indicatorColor="primary"
                        textColor="primary"
                        variant="fullWidth"
                      >
                        <Tab label="当前持仓" />
                        <Tab label="活动委托" />
                      </Tabs>
                      <Box mt={2}>
                        {activeTab === 0 ? (
                          <PositionTable ccy={row.ccy} />
                        ) : (
                          <OrderTable ccy={row.ccy} />
                        )}
                      </Box>
                    </Box>
                  )}
                </TableCell>
              </TableRow>
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
        />
      </Dialog>
    </TableContainer>
  );
};