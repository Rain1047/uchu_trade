import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Switch,
  Collapse,
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';
import { green, blue } from '@material-ui/core/colors';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  table: {
    minWidth: 650,
  },
  stopLossConfig: {
    backgroundColor: green[50],
    '&:hover': {
      backgroundColor: green[100],
    },
  },
  limitConfig: {
    backgroundColor: blue[50],
    '&:hover': {
      backgroundColor: blue[100],
    },
  },
  disabledInput: {
    backgroundColor: theme.palette.action.disabledBackground,
    '& .MuiInputBase-root': {
      color: theme.palette.text.disabled,
    }
  },
  configForm: {
    padding: theme.spacing(2),
    '& > *': {
      margin: theme.spacing(1),
    }
  }
}));

// 自动交易配置组件
const AutoTradeConfig = ({ type, ccy, onSave, existingConfigs = [] }) => {
  const classes = useStyles();
  const [configs, setConfigs] = useState(existingConfigs);

  const handleAddConfig = () => {
    setConfigs([...configs, {
      ccy,
      type,
      signal: 'SMA',
      interval: '',
      percentage: '',
      amount: ''
    }]);
  };

  const handleDeleteConfig = (index) => {
    const newConfigs = configs.filter((_, i) => i !== index);
    setConfigs(newConfigs);
  };

  const handleConfigChange = (index, field, value) => {
    const newConfigs = [...configs];
    newConfigs[index] = {
      ...newConfigs[index],
      [field]: value
    };

    // 如果修改了percentage或amount，清空另一个字段
    if (field === 'percentage' && value) {
      newConfigs[index].amount = '';
    } else if (field === 'amount' && value) {
      newConfigs[index].percentage = '';
    }

    setConfigs(newConfigs);
  };

  return (
    <Box className={classes.configForm}>
      <Typography variant="h6" gutterBottom>
        {type === 'stop_loss' ? '自动止损配置' : '自动限价配置'}
      </Typography>
      {configs.map((config, index) => (
        <Box key={index} display="flex" alignItems="center" mb={2}>
          <TextField
            select
            label="指标"
            value={config.signal || 'SMA'}
            onChange={(e) => handleConfigChange(index, 'signal', e.target.value)}
            style={{ width: 120, marginRight: 8 }}
          >
            <MenuItem value="SMA">SMA</MenuItem>
            <MenuItem value="EMA">EMA</MenuItem>
          </TextField>
          <TextField
            label="时间间隔"
            value={config.interval || ''}
            onChange={(e) => handleConfigChange(index, 'interval', e.target.value)}
            style={{ width: 100, marginRight: 8 }}
          />
          <TextField
            label="百分比"
            value={config.percentage || ''}
            onChange={(e) => handleConfigChange(index, 'percentage', e.target.value)}
            disabled={!!config.amount}
            className={config.amount ? classes.disabledInput : ''}
            style={{ width: 100, marginRight: 8 }}
          />
          <TextField
            label="金额"
            value={config.amount || ''}
            onChange={(e) => handleConfigChange(index, 'amount', e.target.value)}
            disabled={!!config.percentage}
            className={config.percentage ? classes.disabledInput : ''}
            style={{ width: 100, marginRight: 8 }}
          />
          <IconButton onClick={() => handleDeleteConfig(index)}>
            <DeleteIcon />
          </IconButton>
        </Box>
      ))}
      <Box display="flex" justifyContent="space-between" mt={2}>
        <IconButton onClick={handleAddConfig}>
          <AddIcon />
        </IconButton>
        <Button
          variant="contained"
          color="primary"
          onClick={() => onSave(configs)}
        >
          保存
        </Button>
      </Box>
    </Box>
  );
};

// 主资产列表组件
const BalanceList = () => {
  const classes = useStyles();
  const [assets, setAssets] = useState([]);
  const [expandedRows, setExpandedRows] = useState({});

  useEffect(() => {
    const fetchData = () => {
      fetch('http://127.0.0.1:8000/api/balance')
        .then(response => response.json())
        .then(data => {
          if (data.success && data.data) {
            setAssets(data.data);
          }
        })
        .catch(error => {
          console.error('Error fetching assets:', error);
        });
    };

    fetchData();
    const intervalId = setInterval(fetchData, 10000);
    return () => clearInterval(intervalId);
  }, []);

  const handleToggle = (ccy, type) => {
    setExpandedRows(prev => ({
      ...prev,
      [ccy]: {
        ...prev[ccy],
        [type]: !prev[ccy]?.[type]
      }
    }));
  };

  const handleSaveConfig = async (ccy, type, configs) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/balance/auto_config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ccy,
          type,
          configs
        }),
      });

      if (response.ok) {
        // 重新获取资产列表以更新配置
        const balanceResponse = await fetch('http://127.0.0.1:8000/api/balance');
        const balanceData = await balanceResponse.json();
        if (balanceData.success && balanceData.data) {
          setAssets(balanceData.data);
        }
      }
    } catch (error) {
      console.error('Error saving config:', error);
    }
  };

  const calculatePrice = (eq_usd, avail_bal) => {
    return avail_bal && parseFloat(avail_bal) !== 0
      ? (parseFloat(eq_usd) / parseFloat(avail_bal)).toFixed(2)
      : '0';
  };

  return (
    <TableContainer component={Paper}>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell>币种</TableCell>
            <TableCell>可交易数量</TableCell>
            <TableCell>美金价值($)</TableCell>
            <TableCell>当前价格($)</TableCell>
            <TableCell>持仓均价($)</TableCell>
            <TableCell>自动止损</TableCell>
            <TableCell>自动限价</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {assets.map((asset) => (
            <React.Fragment key={asset.ccy}>
              <TableRow>
                <TableCell>{asset.ccy}</TableCell>
                <TableCell>{parseFloat(asset.avail_bal).toFixed(4)}</TableCell>
                <TableCell>{parseFloat(asset.eq_usd).toFixed(2)}</TableCell>
                <TableCell>{calculatePrice(asset.eq_usd, asset.avail_bal)}</TableCell>
                <TableCell>{parseFloat(asset.acc_avg_px || 0).toFixed(2)}</TableCell>
                <TableCell>
                  <Switch
                    checked={asset.stop_loss_switch === 'true'}
                    onChange={() => handleToggle(asset.ccy, 'stop_loss')}
                  />
                </TableCell>
                <TableCell>
                  <Switch
                    checked={asset.limit_order_switch === 'true'}
                    onChange={() => handleToggle(asset.ccy, 'limit')}
                  />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell colSpan={7} style={{ paddingBottom: 0, paddingTop: 0 }}>
                  <Collapse
                    in={expandedRows[asset.ccy]?.stop_loss}
                    timeout="auto"
                    unmountOnExit
                    className={classes.stopLossConfig}
                  >
                    <AutoTradeConfig
                      type="stop_loss"
                      ccy={asset.ccy}
                      onSave={(configs) => handleSaveConfig(asset.ccy, 'stop_loss', configs)}
                      existingConfigs={asset.auto_config_list.filter(config => config.type === 'stop_loss')}
                    />
                  </Collapse>
                  <Collapse
                    in={expandedRows[asset.ccy]?.limit}
                    timeout="auto"
                    unmountOnExit
                    className={classes.limitConfig}
                  >
                    <AutoTradeConfig
                      type="limit"
                      ccy={asset.ccy}
                      onSave={(configs) => handleSaveConfig(asset.ccy, 'limit', configs)}
                      existingConfigs={asset.auto_config_list.filter(config => config.type === 'limit')}
                    />
                  </Collapse>
                </TableCell>
              </TableRow>
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default BalanceList;