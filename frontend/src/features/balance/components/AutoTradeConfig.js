import React, { useState } from 'react';
import {
  Box,
  TextField,
  Typography,
  Button,
  Grid,
  Switch,
  FormControlLabel,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  switchBase: {
    '&.Mui-checked': {
      color: '#FFF',
      '& + .MuiSwitch-track': {
        backgroundColor: '#4CAF50', // 限价绿色
      },
    },
    '&.Mui-checked.Mui-disabled': {
      color: '#FFF',
      '& + .MuiSwitch-track': {
        backgroundColor: '#FF5252', // 止损红色
      },
    },
  },
  track: {
    backgroundColor: '#FF5252', // 默认止损红色
    transition: theme.transitions.create(['background-color'], {
      duration: theme.transitions.duration.shortest,
    }),
  },
  checkedTrack: {
    backgroundColor: '#4CAF50', // 切换到限价绿色
  },
}));

export const AutoTradeConfig = ({ ccy, onSave, onClose, existingConfigs }) => {
  const classes = useStyles();

  // 初始化配置模式（止损或限价）
  const [isStopLoss, setIsStopLoss] = useState(true); // true 为止损，false 为限价

  // 表单状态初始化
  const [config, setConfig] = useState({
    stop_loss_trigger_price: existingConfigs.stop_loss_trigger_price || '',
    stop_loss_exec_price: existingConfigs.stop_loss_exec_price || '',
    stop_loss_indicator: existingConfigs.stop_loss_indicator || '',
    stop_loss_indicator_val: existingConfigs.stop_loss_indicator_val || '',
    stop_loss_percentage: existingConfigs.stop_loss_percentage || '',
    stop_loss_amount: existingConfigs.stop_loss_amount || '',
    limit_order_trigger_price: existingConfigs.limit_order_trigger_price || '',
    limit_order_exec_price: existingConfigs.limit_order_exec_price || '',
    limit_order_indicator: existingConfigs.limit_order_indicator || '',
    limit_order_indicator_val: existingConfigs.limit_order_indicator_val || '',
    limit_order_percentage: existingConfigs.limit_order_percentage || '',
    limit_order_amount: existingConfigs.limit_order_amount || '',
  });

  // 更新表单字段值
  const handleFieldChange = (field, value) => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      [field]: value,
    }));
  };

  // 切换止损/限价模式
  const handleModeChange = () => {
    setIsStopLoss((prev) => !prev);
  };

  return (
    <Box>
      {/* 配置模式选择开关 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">{isStopLoss ? '自动止损配置' : '自动限价配置'}</Typography>
        <FormControlLabel
          control={
            <Switch
              checked={!isStopLoss}
              onChange={handleModeChange}
              color="default"
              classes={{
                switchBase: classes.switchBase,
                track: classes.track,
              }}
            />
          }
          label={isStopLoss ? '止损' : '限价'}
        />
      </Box>

      {/* 动态表单 */}
      <Grid container spacing={2}>
        {/* 公共字段 */}
        <Grid item xs={6}>
          <TextField
            fullWidth
            label={isStopLoss ? '止损触发价格' : '限价触发价格'}
            value={isStopLoss ? config.stop_loss_trigger_price : config.limit_order_trigger_price}
            onChange={(e) =>
              handleFieldChange(
                isStopLoss ? 'stop_loss_trigger_price' : 'limit_order_trigger_price',
                e.target.value
              )
            }
            variant="outlined"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label={isStopLoss ? '止损执行价格' : '限价执行价格'}
            value={isStopLoss ? config.stop_loss_exec_price : config.limit_order_exec_price}
            onChange={(e) =>
              handleFieldChange(
                isStopLoss ? 'stop_loss_exec_price' : 'limit_order_exec_price',
                e.target.value
              )
            }
            variant="outlined"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="指标"
            value={isStopLoss ? config.stop_loss_indicator : config.limit_order_indicator}
            onChange={(e) =>
              handleFieldChange(
                isStopLoss ? 'stop_loss_indicator' : 'limit_order_indicator',
                e.target.value
              )
            }
            variant="outlined"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="指标值"
            value={isStopLoss ? config.stop_loss_indicator_val : config.limit_order_indicator_val}
            onChange={(e) =>
              handleFieldChange(
                isStopLoss ? 'stop_loss_indicator_val' : 'limit_order_indicator_val',
                e.target.value
              )
            }
            variant="outlined"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="百分比"
            value={isStopLoss ? config.stop_loss_percentage : config.limit_order_percentage}
            onChange={(e) =>
              handleFieldChange(
                isStopLoss ? 'stop_loss_percentage' : 'limit_order_percentage',
                e.target.value
              )
            }
            variant="outlined"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="金额"
            value={isStopLoss ? config.stop_loss_amount : config.limit_order_amount}
            onChange={(e) =>
              handleFieldChange(
                isStopLoss ? 'stop_loss_amount' : 'limit_order_amount',
                e.target.value
              )
            }
            variant="outlined"
          />
        </Grid>
      </Grid>

      {/* 操作按钮 */}
      <Box mt={3} display="flex" justifyContent="flex-end">
        <Button onClick={onClose} variant="outlined" style={{ marginRight: 16 }}>
          取消
        </Button>
        <Button
          color="primary"
          variant="contained"
          onClick={() => onSave(config)}
        >
          保存
        </Button>
      </Box>
    </Box>
  );
};
