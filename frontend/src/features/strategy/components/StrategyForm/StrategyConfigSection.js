import React, { useState, useEffect } from 'react';
import {
    Box, Chip,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    Typography,
    CircularProgress
} from '@material-ui/core';
import { useStyles } from './styles';

const StrategyConfigSection = ({
    formData = {},
    onFieldChange,
    viewMode = false,
    errors = {},
    side
}) => {
    const classes = useStyles();
    const [strategies, setStrategies] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchStrategies = async () => {
            setLoading(true);
            try {
                const response = await fetch('http://127.0.0.1:8000/api/strategy/get_strategy_config');
                const data = await response.json();
                if (data.success) {
                    setStrategies(data.data || []);
                }
            } catch (error) {
                console.error('Failed to fetch strategies:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchStrategies();
    }, []);

    const filterStrategies = (type) => {
        return strategies.filter(strategy =>
            strategy.type === type &&
            (!side || strategy.side === side)
        );
    };

    const CustomSelect = ({ children, ...props }) => {
        const [anchorEl, setAnchorEl] = useState(null);

        return (
            <Select
                {...props}
                onOpen={(event) => setAnchorEl(event.currentTarget)}
                onClose={() => setAnchorEl(null)}
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

    if (loading) {
        return <Box display="flex" justifyContent="center"><CircularProgress size={24} /></Box>;
    }

    return (
        <Box>
            <Typography variant="subtitle2" gutterBottom>策略配置</Typography>

            <FormControl
                fullWidth
                variant="outlined"
                className={classes.formControl}
                error={!!errors.entry_st_code}
            >
                <InputLabel>入场策略</InputLabel>
                <CustomSelect
                    label="入场策略"
                    value={formData.entry_st_code || ''}
                    onChange={onFieldChange('entry_st_code')}
                    disabled={viewMode}
                >
                    {filterStrategies('entry').map((strategy) => (
                        <MenuItem key={strategy.name} value={strategy.name}>
                            {strategy.desc}
                        </MenuItem>
                    ))}
                </CustomSelect>
            </FormControl>

            <FormControl
                fullWidth
                variant="outlined"
                className={classes.formControl}
                error={!!errors.exit_st_code}
            >
                <InputLabel>离场策略</InputLabel>
                <CustomSelect
                    label="离场策略"
                    value={formData.exit_st_code || ''}
                    onChange={onFieldChange('exit_st_code')}
                    disabled={viewMode}
                >
                    {filterStrategies('exit').map((strategy) => (
                        <MenuItem key={strategy.name} value={strategy.name}>
                            {strategy.desc}
                        </MenuItem>
                    ))}
                </CustomSelect>
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
                    value={formData.filter_st_code ? formData.filter_st_code.split(',') : []}
                    onChange={(e) => {
                        const value = e.target.value;
                        onFieldChange('filter_st_code')({
                            target: { value: Array.isArray(value) ? value.join(',') : value }
                        });
                    }}
                    disabled={viewMode}
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
                    {filterStrategies('filter').map((strategy) => (
                        <MenuItem key={strategy.name} value={strategy.name}>
                            {strategy.desc}
                        </MenuItem>
                    ))}
                </CustomSelect>
            </FormControl>
        </Box>
    );
};

export default StrategyConfigSection;