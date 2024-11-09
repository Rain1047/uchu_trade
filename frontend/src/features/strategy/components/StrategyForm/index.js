import React from 'react';
import {
  Box,
  Button,
  Divider,
  Drawer,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  CircularProgress,
} from '@material-ui/core';
import {
  Close as CloseIcon,
} from '@material-ui/icons';
import { useStyles } from './styles';
import StopLossSection from './StopLossSection';
import ScheduleSection from './ScheduleSection';
import { useStrategyForm } from '../../hooks/useStrategyForm';
import {
  TRADING_PAIRS,
  TIME_WINDOWS,
  TRADING_SIDES,
} from '../../constants/strategyConfig';

const StrategyForm = ({ open, onClose, strategy = null, viewMode = false }) => {
  const classes = useStyles();
  const {
    formData,
    stopLossConditions,
    selectedDays,
    errors,
    loading,
    handleChange,
    handleStopLossAdd,
    handleStopLossRemove,
    handleStopLossChange,
    handleDayToggle,
    handleSubmit,
  } = useStrategyForm(strategy);

  const handleSave = async () => {
    const success = await handleSubmit();
    if (success) {
      onClose();
    }
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      classes={{ paper: classes.drawerPaper }}
      className={classes.drawer}
    >
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" className={classes.title}>
          <Typography variant="h6">
            {viewMode ? '查看策略' : (strategy ? '编辑策略' : '新建策略')}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* 基本信息 */}
        <Grid container spacing={3} className={classes.formControl}>
          <Grid item xs={6}>
            <TextField
              fullWidth
              variant="outlined"
              label="策略实例名称"
              value={formData.name}
              onChange={handleChange('name')}
              disabled={viewMode}
              error={!!errors.name}
              helperText={errors.name}
            />
          </Grid>
        </Grid>

        {/* 交易配置 */}
        <Grid container spacing={3} className={classes.formControl}>
          <Grid item xs={4}>
            <FormControl fullWidth variant="outlined" error={!!errors.trade_pair}>
              <InputLabel>交易对</InputLabel>
              <Select
                label="交易对"
                value={formData.trade_pair}
                onChange={handleChange('trade_pair')}
                disabled={viewMode}
              >
                {TRADING_PAIRS.map((pair) => (
                  <MenuItem key={pair} value={pair}>{pair}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          {/* ... 其他交易配置字段 ... */}
          <Grid item xs={4}>
            <FormControl fullWidth variant="outlined" error={!!errors.time_frame}>
              <InputLabel>时间窗</InputLabel>
              <Select
                label="时间窗"
                value={formData.time_frame}
                onChange={handleChange('time_frame')}
                disabled={viewMode}
              >
                {TIME_WINDOWS.map((pair) => (
                  <MenuItem key={pair} value={pair}>{pair}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={4}>
            <FormControl fullWidth variant="outlined" error={!!errors.side}>
              <InputLabel>交易方向</InputLabel>
              <Select
                label="交易方向"
                value={formData.side}
                onChange={handleChange('side')}
                disabled={viewMode}
              >
                {TRADING_SIDES.map((pair) => (
                  <MenuItem key={pair} value={pair}>{pair}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Divider className={classes.divider} />

        <Grid container spacing={3} className={classes.formControl}>
        <Grid item xs={6}>
          <TextField
            fullWidth
            variant="outlined"
            label="每笔交易金额"
            type="number"
            value={formData.entry_per_trans}
            onChange={handleChange('entry_per_trans')}
            placeholder="请输入交易金额"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            variant="outlined"
            label="每笔损失交易金额"
            type="number"
            value={formData.loss_per_trans}
            onChange={handleChange('loss_per_trans')}
            placeholder="请输入交易金额"
          />
        </Grid>
        </Grid>

        {/* 止损配置 */}
        <StopLossSection
          conditions={stopLossConditions}
          onAdd={handleStopLossAdd}
          onRemove={handleStopLossRemove}
          onChange={handleStopLossChange}
          viewMode={viewMode}
          errors={errors}
        />

        <Divider className={classes.divider} />

        {/* 调度配置 */}
        <ScheduleSection
          selectedDays={selectedDays}
          onDayToggle={handleDayToggle}
          scheduleTime={formData.schedule_config.time}
          onTimeChange={handleChange('schedule_config.time')}
          viewMode={viewMode}
          errors={errors}
        />

        {/* 提交按钮 */}
        <Box mt={4} className={classes.wrapper}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleSave}
            disabled={loading || viewMode}
          >
            {strategy ? '更新' : '保存'}
          </Button>
          {loading && (
            <CircularProgress size={24} className={classes.buttonProgress} />
          )}
        </Box>
      </Box>
    </Drawer>
  );
};

export default StrategyForm;