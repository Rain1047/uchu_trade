import React, { useState } from 'react';
import {
    Box,
    IconButton,
    MenuItem,
    TextField,
    Tooltip,
} from '@material-ui/core';
import {
    Add as AddIcon,
    Delete as DeleteIcon,
    Check as CheckIcon
} from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import { TRADE_INDICATORS } from '../constants/balanceConstants';

const useStyles = makeStyles((theme) => ({
    configRow: {
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing(2),
        padding: theme.spacing(1),
        marginBottom: theme.spacing(1),
        borderRadius: theme.shape.borderRadius,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
        },
    },
    textField: {
        '& .MuiInputBase-root': {
            color: theme.palette.text.primary,
        },
        '& .MuiOutlinedInput-root': {
            '& fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.2)',
            },
            '&:hover fieldset': {
                borderColor: 'rgba(66, 165, 245, 0.3)',
            },
        },
    },
    addButton: {
        color: theme.palette.text.secondary,
        '&:hover': {
            color: theme.palette.primary.main,
        },
    },
    confirmButton: {
        color: theme.palette.success.main,
        '&:hover': {
            color: theme.palette.success.light,
        },
        '&.Mui-disabled': {
            color: theme.palette.text.disabled,
        },
    },
}));

const ConfigRow = ({ config, onChange, onRemove, onConfirm, isConfirmed }) => {
    const classes = useStyles();
    const [localConfig, setLocalConfig] = useState(config);
    const [isValid, setIsValid] = useState(false);

    const handleChange = (field) => (event) => {
        const value = event.target.value;
        const updates = { ...localConfig, [field]: value };
        if (field === 'percentage' && value) updates.amount = '';
        if (field === 'amount' && value) updates.percentage = '';

        setLocalConfig(updates);
        // Validate if all required fields are filled
        const valid = updates.signal && updates.interval && (updates.percentage || updates.amount);
        setIsValid(valid);
        onChange(updates);
    };

    return (
        <Box className={classes.configRow}>
            <TextField
                select
                size="small"
                variant="outlined"
                label="指标"
                value={localConfig.signal || ''}
                onChange={handleChange('signal')}
                className={classes.textField}
                style={{ width: 120 }}
            >
                {TRADE_INDICATORS.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                        {option.label}
                    </MenuItem>
                ))}
            </TextField>

            <TextField
                size="small"
                variant="outlined"
                label="间隔"
                value={localConfig.interval || ''}
                onChange={handleChange('interval')}
                className={classes.textField}
                style={{ width: 80 }}
            />

            <TextField
                size="small"
                variant="outlined"
                label="百分比"
                value={localConfig.percentage || ''}
                onChange={handleChange('percentage')}
                disabled={!!localConfig.amount}
                className={classes.textField}
                style={{ width: 90 }}
            />

            <TextField
                size="small"
                variant="outlined"
                label="金额"
                value={localConfig.amount || ''}
                onChange={handleChange('amount')}
                disabled={!!localConfig.percentage}
                className={classes.textField}
                style={{ width: 90 }}
            />

            <Tooltip title={isConfirmed ? "已确认" : "确认"}>
                <span>
                    <IconButton
                        size="small"
                        onClick={() => onConfirm(localConfig)}
                        disabled={!isValid || isConfirmed}
                        className={classes.confirmButton}
                    >
                        <CheckIcon fontSize="small" />
                    </IconButton>
                </span>
            </Tooltip>

            <Tooltip title="删除">
                <IconButton size="small" onClick={onRemove}>
                    <DeleteIcon fontSize="small" />
                </IconButton>
            </Tooltip>
        </Box>
    );
};

const TradeConfigForm = ({ configs = [], onChange }) => {
    const classes = useStyles();
    const [localConfigs, setLocalConfigs] = useState(configs);
    const [confirmedConfigs, setConfirmedConfigs] = useState(new Set());

    const handleAdd = () => {
        setLocalConfigs([...localConfigs, {
            signal: '',
            interval: '',
            percentage: '',
            amount: ''
        }]);
    };

    const handleRemove = (index) => {
        const newConfigs = localConfigs.filter((_, i) => i !== index);
        setLocalConfigs(newConfigs);
        const newConfirmed = new Set(confirmedConfigs);
        newConfirmed.delete(index);
        setConfirmedConfigs(newConfirmed);
    };

    const handleChange = (index, updates) => {
        const newConfigs = [...localConfigs];
        newConfigs[index] = updates;
        setLocalConfigs(newConfigs);
    };

    const handleConfirm = (index, config) => {
        // Call the API to save the config
        onChange(config);
        // Mark this config as confirmed
        setConfirmedConfigs(new Set([...confirmedConfigs, index]));
    };

    if (localConfigs.length === 0) {
        return (
            <Tooltip title="添加配置">
                <IconButton className={classes.addButton} onClick={handleAdd}>
                    <AddIcon />
                </IconButton>
            </Tooltip>
        );
    }

    return (
        <Box>
            {localConfigs.map((config, index) => (
                <ConfigRow
                    key={index}
                    config={config}
                    onChange={(updates) => handleChange(index, updates)}
                    onRemove={() => handleRemove(index)}
                    onConfirm={(config) => handleConfirm(index, config)}
                    isConfirmed={confirmedConfigs.has(index)}
                />
            ))}
            <Box display="flex" justifyContent="flex-start" mt={1}>
                <Tooltip title="添加配置">
                    <IconButton className={classes.addButton} onClick={handleAdd}>
                        <AddIcon />
                    </IconButton>
                </Tooltip>
            </Box>
        </Box>
    );
};

export default TradeConfigForm;