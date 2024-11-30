import React from 'react';
import {
    Box, Chip,
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

  const handleFilterChange = (event) => {
    const { value } = event.target;
    onFieldChange('filter_st_code')({ target: { value: Array.isArray(value) ? value.join(',') : value } });
  };

  // Convert comma-separated string to array for Select
  const getFilterValues = () => {
    if (!formData.filter_st_code) return [];
    return formData.filter_st_code.split(',').filter(Boolean);
  };

  const CustomSelect = ({ children, ...props }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Select
      {...props}
      onOpen={handleOpen}
      onClose={handleClose}
      MenuProps={{
        anchorEl,
        anchorOrigin: {
          vertical: 'bottom',
          horizontal: 'left',
        },
        transformOrigin: {
          vertical: 'top',
          horizontal: 'left',
        },
        getContentAnchorEl: null,
      }}
    >
      {children}
    </Select>
  );
};


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
        <CustomSelect
          multiple
          label="过滤策略"
          value={getFilterValues()}
          onChange={handleFilterChange}
          disabled={viewMode}
          className={classes.select}
          renderValue={(selected) => (
            <Box className={classes.chips}>
              {selected.map((value) => (
                <Chip
                  key={value}
                  label={value}
                  className={classes.chip}
                  size="small"
                />
              ))}
            </Box>
          )}
        >
          {strategies.filterStrategies.map((strategy) => (
            <MenuItem key={strategy} value={strategy}>
              {strategy}
            </MenuItem>
          ))}
        </CustomSelect>
      </FormControl>
    </>
  );
};

export default StrategyConfigSection;