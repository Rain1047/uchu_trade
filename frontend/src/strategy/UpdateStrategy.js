import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
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
  Chip,
  Paper,
} from '@material-ui/core';
import {
  Add as AddIcon,
  Close as CloseIcon,
  Delete as DeleteIcon
} from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  drawer: {
    width: '50%',
    minWidth: 600,
    maxWidth: 800,
  },
  drawerPaper: {
    width: '50%',
    minWidth: 600,
    maxWidth: 800,
    padding: theme.spacing(3),
  },
  title: {
    marginBottom: theme.spacing(3),
  },
  formControl: {
    marginBottom: theme.spacing(3),
  },
  divider: {
    margin: theme.spacing(4, 0),
  },
  weekDayChip: {
    margin: theme.spacing(0.5),
  },
  stopLossItem: {
    marginBottom: theme.spacing(2),
    padding: theme.spacing(2),
    backgroundColor: theme.palette.background.default,
  },
  addButton: {
    marginBottom: theme.spacing(3),
  }
}));

const weekDays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 },
];

const UpdateStrategy = () => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [stopLossConditions, setStopLossConditions] = useState([]);
  const [selectedDays, setSelectedDays] = useState([]);
  const [tradeAmount, setTradeAmount] = useState('');
  const [tradeLossAmount, setTradeLossAmount] = useState('');
  const [strategyName, setStrategyName] = useState('');

  // Mock data - 替换为实际API数据
  const mockData = {
    tradingPairs: ['BTC-USDT', 'ETH-USDT', 'BNB-USDT'],
    timeWindows: ['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
    entryStrategies: ['Strategy1', 'Strategy2', 'Strategy3'],
    exitStrategies: ['Exit1', 'Exit2', 'Exit3'],
    stopLossTypes: ['定价止损', '跟踪止损', '百分比止损'],
    filterStrategies: ['Filter1', 'Filter2', 'Filter3'],
    tradingSides: ['long', 'short']
  };

  const handleToggleDrawer = (open) => {
    setOpen(open);
  };

  const handleAddStopLoss = () => {
    setStopLossConditions([
      ...stopLossConditions,
      { type: '', value: '' }
    ]);
  };

  const handleRemoveStopLoss = (index) => {
    const newConditions = [...stopLossConditions];
    newConditions.splice(index, 1);
    setStopLossConditions(newConditions);
  };

  const handleStopLossChange = (index, field, value) => {
    const newConditions = [...stopLossConditions];
    newConditions[index] = {
      ...newConditions[index],
      [field]: value
    };
    setStopLossConditions(newConditions);
  };

  const handleWeekDayToggle = (day) => {
    const currentIndex = selectedDays.indexOf(day);
    const newSelectedDays = [...selectedDays];

    if (currentIndex === -1) {
      newSelectedDays.push(day);
    } else {
      newSelectedDays.splice(currentIndex, 1);
    }

    setSelectedDays(newSelectedDays);
  };

  const handleTradeAmountChange = (event) => {
    setTradeAmount(event.target.value);
  };

  const handleStrategyNameChange = (event) => {
    setStrategyName(event.target.value);
  };

  const handleTradeLossAmountChange = (event) => {  // 新增处理函数
    setTradeLossAmount(event.target.value);
  };

  const formContent = (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" className={classes.title}>
        <Typography variant="h6">新建交易策略</Typography>
        <IconButton onClick={() => handleToggleDrawer(false)}>
          <CloseIcon />
        </IconButton>
      </Box>

      <Grid container spacing={3} className={classes.formControl}>
        <Grid item xs={6}>
          <TextField
            fullWidth
            variant="outlined"
            label="策略实例名称"
            value={strategyName}
            onChange={handleStrategyNameChange}
            placeholder="请输入策略实例名称"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} className={classes.formControl}>
        <Grid item xs={4}>
          <FormControl fullWidth variant="outlined">
            <InputLabel>交易对</InputLabel>
            <Select label="交易对">
              {mockData.tradingPairs.map((pair) => (
                <MenuItem key={pair} value={pair}>{pair}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={4}>
          <FormControl fullWidth variant="outlined">
            <InputLabel>时间窗</InputLabel>
            <Select label="时间窗">
              {mockData.timeWindows.map((window) => (
                <MenuItem key={window} value={window}>{window}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={4}>
          <FormControl fullWidth variant="outlined">
            <InputLabel>交易方向</InputLabel>
            <Select label="时间窗">
              {mockData.tradingSides.map((window) => (
                <MenuItem key={window} value={window}>{window}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <Grid container spacing={3} className={classes.formControl}>
        <Grid item xs={6}>
          <TextField
            fullWidth
            variant="outlined"
            label="每笔交易金额"
            type="number"
            value={tradeAmount}
            onChange={handleTradeAmountChange}
            placeholder="请输入交易金额"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            variant="outlined"
            label="每笔损失交易金额"
            type="number"
            value={tradeLossAmount}
            onChange={handleTradeLossAmountChange}
            placeholder="请输入交易金额"
          />
        </Grid>
      </Grid>

      <Divider className={classes.divider} />

      <Typography variant="subtitle2" gutterBottom>策略配置</Typography>

      <FormControl fullWidth variant="outlined" className={classes.formControl}>
        <InputLabel>入场策略</InputLabel>
        <Select label="入场策略">
          {mockData.entryStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>{strategy}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth variant="outlined" className={classes.formControl}>
        <InputLabel>离场策略</InputLabel>
        <Select label="离场策略">
          {mockData.exitStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>{strategy}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth variant="outlined" className={classes.formControl}>
        <InputLabel>过滤策略</InputLabel>
        <Select label="过滤策略">
          {mockData.filterStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>{strategy}</MenuItem>
          ))}
        </Select>
      </FormControl>

        <Button
        variant="outlined"
        color="primary"
        startIcon={<AddIcon />}
        onClick={handleAddStopLoss}
        className={classes.addButton}
      >
        添加止损条件
      </Button>

      {stopLossConditions.map((condition, index) => (
        <Paper key={index} className={classes.stopLossItem}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={5}>
              <FormControl fullWidth variant="outlined">
                <InputLabel>止损类型</InputLabel>
                <Select
                  label="止损类型"
                  value={condition.type}
                  onChange={(e) => handleStopLossChange(index, 'type', e.target.value)}
                >
                  {mockData.stopLossTypes.map((type) => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={5}>
              <TextField
                fullWidth
                variant="outlined"
                label="止损值"
                value={condition.value}
                onChange={(e) => handleStopLossChange(index, 'value', e.target.value)}
              />
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={() => handleRemoveStopLoss(index)}>
                <DeleteIcon />
              </IconButton>
            </Grid>
          </Grid>
        </Paper>
      ))}

      <Divider className={classes.divider} />

      <Typography variant="subtitle1" gutterBottom>调度配置</Typography>

      <Box className={classes.formControl}>
        <Typography variant="body2" gutterBottom>每周运行天数</Typography>
        <Box>
          {weekDays.map((day) => (
            <Chip
              key={day.value}
              label={day.label}
              clickable
              color={selectedDays.includes(day.value) ? "primary" : "default"}
              onClick={() => handleWeekDayToggle(day.value)}
              className={classes.weekDayChip}
            />
          ))}
        </Box>
      </Box>

      <Box className={classes.formControl}>
        <TextField
          fullWidth
          variant="outlined"
          label="每天运行时间"
          placeholder="例如: 0-8,9-10"
          helperText="请使用格式: 0-8,9-10"
        />
      </Box>

      <Box mt={4}>
        <Button variant="contained" color="primary" fullWidth>
          保存
        </Button>
      </Box>
    </Box>
  );

  return (
    <Container>
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleToggleDrawer(true)}
        >
          新建策略
        </Button>
      </Box>

      <Drawer
        anchor="right"
        open={open}
        onClose={() => handleToggleDrawer(false)}
        classes={{
          paper: classes.drawerPaper,
        }}
        className={classes.drawer}
      >
        {formContent}
      </Drawer>
    </Container>
  );
};

export default UpdateStrategy;