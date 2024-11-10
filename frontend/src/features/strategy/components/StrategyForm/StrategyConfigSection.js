import React from 'react';
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@material-ui/core';
import { useStyles } from './styles';

const StrategyConfigSection = ({
  formData = {},
  onFieldChange,
  viewMode = false,
  errors = {},
  strategies = {
    entryStrategies: [],
    exitStrategies: [],
    filterStrategies: []
  }
}) => {
  const classes = useStyles();

  return (
    <>
      <Typography variant="subtitle2" gutterBottom>策略配置</Typography>

      <FormControl
        fullWidth
        variant="outlined"
        className={classes.formControl}
        error={!!errors.entry_st_code}
      >
        <InputLabel>入场策略</InputLabel>
        <Select
          label="入场策略"
          value={formData.entry_st_code || ''}
          onChange={onFieldChange('entry_st_code')}
          disabled={viewMode}
        >
          {strategies.entryStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>
              {strategy}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl
        fullWidth
        variant="outlined"
        className={classes.formControl}
        error={!!errors.exit_st_code}
      >
        <InputLabel>离场策略</InputLabel>
        <Select
          label="离场策略"
          value={formData.exit_st_code || ''}
          onChange={onFieldChange('exit_st_code')}
          disabled={viewMode}
        >
          {strategies.exitStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>
              {strategy}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl
        fullWidth
        variant="outlined"
        className={classes.formControl}
        error={!!errors.filter_st_code}
      >
        <InputLabel>过滤策略</InputLabel>
        <Select
          label="过滤策略"
          value={formData.filter_st_code || ''}
          onChange={onFieldChange('filter_st_code')}
          disabled={viewMode}
        >
          {strategies.filterStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>
              {strategy}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </>
  );
};

export default StrategyConfigSection;