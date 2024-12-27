import React, { useState, useEffect } from 'react';
import {
    Box,
    TextField,
    MenuItem,
    IconButton,
    Button,
    makeStyles
} from '@material-ui/core';
import { Add as AddIcon, Delete as DeleteIcon } from '@material-ui/icons';
import { TRADE_INDICATORS } from '../constants/balanceConstants';

const useStyles = makeStyles((theme) => ({
    form: {
        width: '100%',
        marginTop: theme.spacing(2)
    },
    configRow: {
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing(2),
        marginBottom: theme.spacing(2)
    },
    addButton: {
        marginTop: theme.spacing(2)
    }
}));

const TradeConfigForm = ({ type, initialConfigs = [], onSave }) => {
    const classes = useStyles();
    const [configs, setConfigs] = useState(initialConfigs);

    const handleAddConfig = () => {
        setConfigs([...configs, {
            indicator: '',
            interval: '',
            amount: ''
        }]);
    };

    const handleRemoveConfig = (index) => {
        setConfigs(configs.filter((_, i) => i !== index));
    };

    const handleConfigChange = (index, field, value) => {
        const newConfigs = [...configs];
        newConfigs[index] = { ...newConfigs[index], [field]: value };
        setConfigs(newConfigs);
    };

    return (
        <form className={classes.form}>
            {configs.map((config, index) => (
                <Box key={index} className={classes.configRow}>
                    <TextField
                        select
                        label="指标"
                        value={config.indicator}
                        onChange={(e) => handleConfigChange(index, 'indicator', e.target.value)}
                    >
                        {TRADE_INDICATORS.map(indicator => (
                            <MenuItem key={indicator.value} value={indicator.value}>
                                {indicator.label}
                            </MenuItem>
                        ))}
                    </TextField>
                    <TextField
                        label="间隔"
                        type="number"
                        value={config.interval}
                        onChange={(e) => handleConfigChange(index, 'interval', e.target.value)}
                    />
                    <TextField
                        label="金额"
                        type="number"
                        value={config.amount}
                        onChange={(e) => handleConfigChange(index, 'amount', e.target.value)}
                    />
                    <IconButton onClick={() => handleRemoveConfig(index)}>
                        <DeleteIcon />
                    </IconButton>
                </Box>
            ))}
            <Button
                startIcon={<AddIcon />}
                onClick={handleAddConfig}
                className={classes.addButton}
                variant="outlined"
                fullWidth
            >
                添加配置
            </Button>
        </form>
    );
};

export default TradeConfigForm;