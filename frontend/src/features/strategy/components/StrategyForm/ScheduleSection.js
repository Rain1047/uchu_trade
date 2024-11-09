import React from 'react';
import {
  Box,
  Chip,
  TextField,
  Typography,
} from '@material-ui/core';
import { WEEK_DAYS } from '../../constants/strategyConfig';
import { useStyles } from './styles';

const ScheduleSection = ({
  selectedDays = [],  // 添加默认值
  onDayToggle = () => {},
  scheduleTime = '',
  onTimeChange = () => {},
  viewMode = false,
  errors = {}
}) => {
  const classes = useStyles();

  return (
    <>
      <Typography variant="subtitle1" gutterBottom>调度配置</Typography>

      <Box className={classes.formControl}>
        <Typography variant="body2" gutterBottom>每周运行天数</Typography>
        <Box>
          {WEEK_DAYS.map((day) => (
            <Chip
              key={day.value}
              label={day.label}
              clickable={!viewMode}
              color={selectedDays.includes(day.value) ? "primary" : "default"}
              onClick={() => !viewMode && onDayToggle(day.value)}
              className={classes.weekDayChip}
            />
          ))}
        </Box>
        {errors.schedule_days && (
          <Typography className={classes.error}>
            {errors.schedule_days}
          </Typography>
        )}
      </Box>

      <Box className={classes.formControl}>
        <TextField
          fullWidth
          variant="outlined"
          label="每天运行时间"
          placeholder="例如: 0-8,9-10"
          helperText={errors.schedule_time || "请使用格式: 0-8,9-10"}
          value={scheduleTime}
          onChange={onTimeChange}
          disabled={viewMode}
          error={!!errors.schedule_time}
        />
      </Box>
    </>
  );
};

export default ScheduleSection;