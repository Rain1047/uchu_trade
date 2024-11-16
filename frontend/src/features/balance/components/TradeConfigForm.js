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
        gap: theme.spacing(1),
        padding: theme.spacing(0.5),
        marginBottom: theme.spacing(0.5),
        borderRadius: theme.shape.borderRadius,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
        },
    },
    textField: {
        '& .MuiInputBase-root': {
            color: theme.palette.text.primary,
            fontSize: '0.813rem', // 13px
        },
        '& .MuiInputLabel-root': {
            fontSize: '0.75rem', // 12px
        },
        '& .MuiOutlinedInput-root': {
            '& fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.2)',
            },
            '&:hover fieldset': {
                borderColor: 'rgba(66, 165, 245, 0.3)',
            },
        },
        // 减小输入框的高度
        '& .MuiOutlinedInput-input': {
            padding: '7px 14px',
        }
    },
    addButton: {
        color: theme.palette.text.secondary,
        padding: 4,
        '&:hover': {
            color: theme.palette.primary.main,
        },
    },
    confirmButton: {
        color: theme.palette.success.main,
        padding: 4,
        '&:hover': {
            color: theme.palette.success.light,
        },
        '&.Mui-disabled': {
            color: theme.palette.text.disabled,
        },
    },
    typeIndicator: {
        width: 24,
        height: 24,
        borderRadius: 4,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '0.75rem',
        color: theme.palette.common.white,
        fontWeight: 500,
        userSelect: 'none', // 防止文字被选中
    },
    menuItem: {
        fontSize: '0.813rem', // 下拉菜单项的字体大小
    },

    stopLossIndicator: {
        backgroundColor: 'rgba(239,40,180,0.42)', // 使用粉色
    },
    limitOrderIndicator: {
        backgroundColor: 'rgba(4,115,72,0.44)', // 使用绿色
    }
}));

const ConfigRow = ({ config, onChange, onRemove, onConfirm, isConfirmed, type }) => {
    const classes = useStyles();
    const [localConfig, setLocalConfig] = useState(config);
    const [confirmedConfigs, setConfirmedConfigs] = useState(new Set());
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
            <Box
                className={`${classes.typeIndicator} ${
                    type === 'stop_loss' ? classes.stopLossIndicator : classes.limitOrderIndicator
                }`}
            >
                {type === 'stop_loss' ? 'SL' : 'LO'}
            </Box>
            <TextField
                select
                size="small"
                variant="outlined"
                label="指标"
                value={localConfig.signal || ''}
                onChange={handleChange('signal')}
                className={classes.textField}
                style={{ width: 110 }}
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
                style={{ width: 70 }}
            />

            <TextField
                size="small"
                variant="outlined"
                label="百分比"
                value={localConfig.percentage || ''}
                onChange={handleChange('percentage')}
                disabled={!!localConfig.amount}
                className={classes.textField}
                style={{ width: 80 }}
            />

            <TextField
                size="small"
                variant="outlined"
                label="金额"
                value={localConfig.amount || ''}
                onChange={handleChange('amount')}
                disabled={!!localConfig.percentage}
                className={classes.textField}
                style={{ width: 80 }}
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

const TradeConfigForm = ({ configs = [], onChange, type }) => {
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
                    type={type}
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