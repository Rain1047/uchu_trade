import React from 'react';
import {
    Box,
    Button,
    IconButton,
    MenuItem,
    TextField,
    Typography,
} from '@material-ui/core';
import {
    Add as AddIcon,
    Delete as DeleteIcon
} from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import { TRADE_INDICATORS } from '../constants/balanceConstants';

const useStyles = makeStyles((theme) => ({
    configForm: {
        padding: theme.spacing(2),
    },
    configRow: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: theme.spacing(2),
        '& > *:not(:last-child)': {
            marginRight: theme.spacing(2),
        }
    },
    disabledInput: {
        backgroundColor: theme.palette.action.disabledBackground,
        '& .MuiInputBase-root': {
            color: theme.palette.text.disabled,
        }
    },
}));

const TradeConfigForm = ({ config, onChange, onRemove }) => {
    const classes = useStyles();

    const handleChange = (field) => (event) => {
        const value = event.target.value;
        const updates = {
            ...config,
            [field]: value,
        };

        // Handle mutual exclusivity between percentage and amount
        if (field === 'percentage' && value) {
            updates.amount = '';
        } else if (field === 'amount' && value) {
            updates.percentage = '';
        }

        onChange(updates);
    };

    return (
        <Box className={classes.configRow}>
            <TextField
                select
                label="指标"
                value={config.signal || 'SMA'}
                onChange={handleChange('signal')}
                style={{ width: 120 }}
            >
                {TRADE_INDICATORS.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                        {option.label}
                    </MenuItem>
                ))}
            </TextField>

            <TextField
                label="时间间隔"
                value={config.interval || ''}
                onChange={handleChange('interval')}
                style={{ width: 100 }}
            />

            <TextField
                label="百分比"
                value={config.percentage || ''}
                onChange={handleChange('percentage')}
                disabled={!!config.amount}
                className={config.amount ? classes.disabledInput : ''}
                style={{ width: 100 }}
            />

            <TextField
                label="金额"
                value={config.amount || ''}
                onChange={handleChange('amount')}
                disabled={!!config.percentage}
                className={config.percentage ? classes.disabledInput : ''}
                style={{ width: 100 }}
            />

            <IconButton onClick={onRemove} color="secondary">
                <DeleteIcon />
            </IconButton>
        </Box>
    );
};

export default TradeConfigForm;