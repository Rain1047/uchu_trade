import React from 'react';
import {
    Box,
    IconButton,
    MenuItem,
    TextField,
    Tooltip,
} from '@material-ui/core';
import {
    Add as AddIcon,
    Delete as DeleteIcon
} from '@material-ui/icons';
import { makeStyles, alpha } from '@material-ui/core/styles';
import { TRADE_INDICATORS } from '../constants/balanceConstants';

const useStyles = makeStyles((theme) => ({
    configRow: {
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing(2),
        padding: theme.spacing(1),
        marginBottom: theme.spacing(1),
        borderRadius: theme.shape.borderRadius,
        backgroundColor: alpha(theme.palette.background.paper, 0.05),
        '&:hover': {
            backgroundColor: alpha(theme.palette.background.paper, 0.08),
        },
    },
    textField: {
        '& .MuiInputBase-root': {
            color: theme.palette.text.primary,
        },
        '& .MuiOutlinedInput-root': {
            '& fieldset': {
                borderColor: alpha(theme.palette.divider, 0.2),
            },
            '&:hover fieldset': {
                borderColor: alpha(theme.palette.primary.main, 0.3),
            },
        },
    },
    addButton: {
        color: theme.palette.text.secondary,
        '&:hover': {
            color: theme.palette.primary.main,
        },
    },
}));

const ConfigRow = ({ config, onChange, onRemove }) => {
    const classes = useStyles();

    const handleChange = (field) => (event) => {
        const value = event.target.value;
        const updates = { ...config, [field]: value };
        if (field === 'percentage' && value) updates.amount = '';
        if (field === 'amount' && value) updates.percentage = '';
        onChange(updates);
    };

    return (
        <Box className={classes.configRow}>
            <TextField
                select
                size="small"
                variant="outlined"
                label="指标"
                value={config.signal || 'SMA'}
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
                value={config.interval || ''}
                onChange={handleChange('interval')}
                className={classes.textField}
                style={{ width: 80 }}
            />

            <TextField
                size="small"
                variant="outlined"
                label="百分比"
                value={config.percentage || ''}
                onChange={handleChange('percentage')}
                disabled={!!config.amount}
                className={classes.textField}
                style={{ width: 90 }}
            />

            <TextField
                size="small"
                variant="outlined"
                label="金额"
                value={config.amount || ''}
                onChange={handleChange('amount')}
                disabled={!!config.percentage}
                className={classes.textField}
                style={{ width: 90 }}
            />

            <Tooltip title="删除">
                <IconButton size="small" onClick={onRemove}>
                    <DeleteIcon fontSize="small" />
                </IconButton>
            </Tooltip>
        </Box>
    );
};

const TradeConfigForm = ({ configs = [], onAdd, onRemove, onChange }) => {
    const classes = useStyles();

    if (configs.length === 0) {
        return (
            <Tooltip title="添加配置">
                <IconButton className={classes.addButton} onClick={onAdd}>
                    <AddIcon />
                </IconButton>
            </Tooltip>
        );
    }

    return (
        <Box>
            {configs.map((config, index) => (
                <ConfigRow
                    key={index}
                    config={config}
                    onChange={(updates) => onChange(index, updates)}
                    onRemove={() => onRemove(index)}
                />
            ))}
            <Box display="flex" justifyContent="flex-start" mt={1}>
                <Tooltip title="添加配置">
                    <IconButton className={classes.addButton} onClick={onAdd}>
                        <AddIcon />
                    </IconButton>
                </Tooltip>
            </Box>
        </Box>
    );
};

export default TradeConfigForm;