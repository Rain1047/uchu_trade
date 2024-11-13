import React from 'react';
import {
  Button,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
} from '@material-ui/core';
import {
  Add as AddIcon,
  Delete as DeleteIcon
} from '@material-ui/icons';
import { STOP_LOSS_TYPES } from '../../constants/strategyConfig';
import { useStyles } from './styles';

const StopLossSection = ({
  conditions = [],  // 添加默认值
  onAdd = () => {},
  onRemove = () => {},
  onChange = () => {},
  viewMode = false,
  errors = {}
}) => {
  const classes = useStyles();

  return (
    <>
      <Typography variant="subtitle2" gutterBottom>止损配置</Typography>

      <Button
        variant="outlined"
        color="primary"
        startIcon={<AddIcon />}
        onClick={onAdd}
        className={classes.addButton}
        disabled={viewMode}
      >
        添加止损条件
      </Button>

      {conditions.map((condition, index) => (
        <Paper key={index} className={classes.stopLossItem}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={5}>
              <FormControl fullWidth variant="outlined" error={!!errors[`stopLoss_${index}_type`]}>
                <InputLabel>止损类型</InputLabel>
                <Select
                  label="止损类型"
                  value={condition.type}
                  onChange={(e) => onChange(index, 'type', e.target.value)}
                  disabled={viewMode}
                >
                  {STOP_LOSS_TYPES.map((type) => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
                {errors[`stopLoss_${index}_type`] && (
                  <Typography className={classes.error}>
                    {errors[`stopLoss_${index}_type`]}
                  </Typography>
                )}
              </FormControl>
            </Grid>
            <Grid item xs={5}>
              <TextField
                fullWidth
                variant="outlined"
                label="止损值"
                value={condition.value}
                onChange={(e) => onChange(index, 'value', e.target.value)}
                disabled={viewMode}
                error={!!errors[`stopLoss_${index}_value`]}
                helperText={errors[`stopLoss_${index}_value`]}
              />
            </Grid>
            <Grid item xs={2}>
              {!viewMode && (
                <IconButton onClick={() => onRemove(index)}>
                  <DeleteIcon />
                </IconButton>
              )}
            </Grid>
          </Grid>
        </Paper>
      ))}
    </>
  );
};

export default StopLossSection;