import React, { useState } from 'react';
import {
    Box,
    Button,
    IconButton,
    Typography,
} from '@material-ui/core';
import { Add as AddIcon } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import TradeConfigForm from './TradeConfigForm';

const useStyles = makeStyles((theme) => ({
    root: {
        padding: theme.spacing(2),
    },
    controls: {
        display: 'flex',
        justifyContent: 'space-between',
        marginTop: theme.spacing(2),
    }
}));

const AutoTradeConfig = ({ type, ccy, onSave, existingConfigs = [], onClose }) => {
    const classes = useStyles();
    const [configs, setConfigs] = useState(existingConfigs);

    const handleAddConfig = () => {
        setConfigs([...configs, {
            ccy,
            type,
            signal: 'SMA',
            interval: '',
            percentage: '',
            amount: ''
        }]);
    };

    const handleUpdateConfig = (index, updatedConfig) => {
        const newConfigs = [...configs];
        newConfigs[index] = updatedConfig;
        setConfigs(newConfigs);
    };

    const handleRemoveConfig = (index) => {
        setConfigs(configs.filter((_, i) => i !== index));
    };

    const handleSave = async () => {
        await onSave(configs);
        onClose?.();
    };

    return (
        <Box className={classes.root}>
            <Typography variant="h6" gutterBottom>
                {type === 'stop_loss' ? '自动止损配置' : '自动限价配置'}
            </Typography>

            {configs.map((config, index) => (
                <TradeConfigForm
                    key={index}
                    config={config}
                    onChange={(updatedConfig) => handleUpdateConfig(index, updatedConfig)}
                    onRemove={() => handleRemoveConfig(index)}
                />
            ))}

            <Box className={classes.controls}>
                <IconButton onClick={handleAddConfig} color="primary">
                    <AddIcon />
                </IconButton>

                <Box>
                    <Button
                        variant="outlined"
                        color="secondary"
                        onClick={onClose}
                        style={{ marginRight: 8 }}
                    >
                        取消
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                    >
                        保存
                    </Button>
                </Box>
            </Box>
        </Box>
    );
};

export default AutoTradeConfig;