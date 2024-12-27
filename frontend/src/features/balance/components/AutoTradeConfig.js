import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  FormControlLabel,
  TextField,
  Grid,
  IconButton,
} from '@material-ui/core';
import Switch from '@mui/material/Switch';
import { Add as AddIcon, Delete as DeleteIcon } from '@material-ui/icons';

export const AutoTradeConfig = ({ ccy, onSave, onClose, existingConfigs }) => {
  const [isStopLoss, setIsStopLoss] = useState(true); // true 为止损，false 为限价
  const [stopLossConfigs, setStopLossConfigs] = useState(
    existingConfigs.stop_loss_spot_trade_configs || []
  );
  const [limitOrderConfigs, setLimitOrderConfigs] = useState(
    existingConfigs.limit_order_spot_trade_configs || []
  );
  const [newConfig, setNewConfig] = useState(null); // 用于存储新增配置的表单内容

  // 切换止损/限价模式
  const handleModeChange = () => {
    setIsStopLoss((prev) => !prev);
  };

  // 删除配置（仅前端显示删除）
  const handleDeleteConfig = (index) => {
    if (isStopLoss) {
      setStopLossConfigs((prev) => prev.filter((_, i) => i !== index));
    } else {
      setLimitOrderConfigs((prev) => prev.filter((_, i) => i !== index));
    }
  };

  // 新增配置
  const handleAddConfig = () => {
    setNewConfig({
      id: null,
      ccy,
      type: isStopLoss ? 'stop_loss' : 'limit_order',
      indicator: '',
      indicator_val: '',
      target_price: '',
      percentage: '',
      amount: '',
      switch: '0',
      exec_nums: 1,
      is_del: '0',
    });
  };

  // 保存新增配置
  const handleSaveNewConfig = () => {
    if (newConfig) {
      if (isStopLoss) {
        setStopLossConfigs((prev) => [...prev, newConfig]);
      } else {
        setLimitOrderConfigs((prev) => [...prev, newConfig]);
      }
      setNewConfig(null);
    }
  };

  return (
    <Box>
      {/* 配置模式选择开关 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">{isStopLoss ? '止损配置' : '限价配置'}</Typography>
        <FormControlLabel
          control={
            <Switch
              checked={!isStopLoss}
              onChange={handleModeChange}
              color="primary"
            />
          }
          label={isStopLoss ? '止损' : '限价'}
        />
      </Box>

      {/* 配置列表 */}
      <Box mb={3}>
        {isStopLoss ? (
          stopLossConfigs.length > 0 ? (
            stopLossConfigs.map((config, index) => (
              <Box
                key={index}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                mb={2}
              >
                <Typography>
                  指标: {config.indicator || '无'}, 值: {config.indicator_val || '无'}, 金额:{' '}
                  {config.amount || '无'}
                </Typography>
                <IconButton onClick={() => handleDeleteConfig(index)}>
                  <DeleteIcon color="error" />
                </IconButton>
              </Box>
            ))
          ) : (
            <Typography color="textSecondary">当前无止损配置</Typography>
          )
        ) : limitOrderConfigs.length > 0 ? (
          limitOrderConfigs.map((config, index) => (
            <Box
              key={index}
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              mb={2}
            >
              <Typography>
                指标: {config.indicator || '无'}, 值: {config.indicator_val || '无'}, 金额:{' '}
                {config.amount || '无'}
              </Typography>
              <IconButton onClick={() => handleDeleteConfig(index)}>
                <DeleteIcon color="error" />
              </IconButton>
            </Box>
          ))
        ) : (
          <Typography color="textSecondary">当前无限价配置</Typography>
        )}
      </Box>

      {/* 新增配置表单 */}
      {newConfig && (
        <Box mb={3}>
          <Typography variant="subtitle1">新增配置</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="指标"
                value={newConfig.indicator}
                onChange={(e) =>
                  setNewConfig((prev) => ({ ...prev, indicator: e.target.value }))
                }
                variant="outlined"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="指标值"
                value={newConfig.indicator_val}
                onChange={(e) =>
                  setNewConfig((prev) => ({ ...prev, indicator_val: e.target.value }))
                }
                variant="outlined"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="金额"
                value={newConfig.amount}
                onChange={(e) =>
                  setNewConfig((prev) => ({ ...prev, amount: e.target.value }))
                }
                variant="outlined"
              />
            </Grid>
          </Grid>
          <Box display="flex" justifyContent="flex-end" mt={2}>
            <Button
              onClick={() => setNewConfig(null)}
              variant="outlined"
              style={{ marginRight: 16 }}
            >
              取消
            </Button>
            <Button color="primary" variant="contained" onClick={handleSaveNewConfig}>
              保存
            </Button>
          </Box>
        </Box>
      )}

      {/* 添加配置按钮 */}
      {!newConfig && (
        <Box display="flex" justifyContent="center" mb={3}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleAddConfig}
          >
            添加配置
          </Button>
        </Box>
      )}

      {/* 操作按钮 */}
      <Box mt={3} display="flex" justifyContent="flex-end">
        <Button onClick={onClose} variant="outlined" style={{ marginRight: 16 }}>
          取消
        </Button>
        <Button
          color="primary"
          variant="contained"
          onClick={() =>
            onSave({
              stop_loss_spot_trade_configs: stopLossConfigs,
              limit_order_spot_trade_configs: limitOrderConfigs,
            })
          }
        >
          保存
        </Button>
      </Box>
    </Box>
  );
};
