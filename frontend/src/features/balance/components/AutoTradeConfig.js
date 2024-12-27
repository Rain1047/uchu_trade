import React, { useState } from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Typography,
    IconButton,
    TextField,
    MenuItem,
    Divider,
    Tooltip,
} from '@material-ui/core';
import {
    Add as AddIcon,
    Delete as DeleteIcon,
    Close as CloseIcon
} from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import { TRADE_INDICATORS } from '../constants/balanceConstants';

const useStyles = makeStyles((theme) => ({
    dialogTitle: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: theme.spacing(2),
    },
    closeButton: {
        position: 'absolute',
        right: theme.spacing(1),
        top: theme.spacing(1),
    },
    content: {
        padding: theme.spacing(2),
        minHeight: '300px',
    },
    configItem: {
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing(2),
        marginBottom: theme.spacing(2),
        padding: theme.spacing(2),
        backgroundColor: theme.palette.action.hover,
        borderRadius: theme.shape.borderRadius,
    },
    addButton: {
        marginTop: theme.spacing(2),
    },
    typeIndicator: {
        padding: theme.spacing(0.5, 1),
        borderRadius: theme.shape.borderRadius,
        fontWeight: 500,
        fontSize: '0.75rem',
    },
    stopLossIndicator: {
        backgroundColor: theme.palette.error.dark,
        color: theme.palette.error.contrastText,
    },
    limitOrderIndicator: {
        backgroundColor: theme.palette.success.dark,
        color: theme.palette.success.contrastText,
    }
}));

export const AutoTradeConfig = ({
    type,
    ccy,
    onSave,
    onClose,
    existingConfigs = []
}) => {
    const classes = useStyles();
    const [configs, setConfigs] = useState(
        existingConfigs.filter(config => config.type === type)
    );

    const getTypeLabel = () => {
        return type === 'stop_loss' ? '止损' : '限价';
    };

    const getInitialConfig = () => ({
        type,
        indicator: '',
        interval: '',
        percentage: '',
        amount: '',
        ccy
    });

    const handleAddConfig = () => {
        setConfigs([...configs, getInitialConfig()]);
    };

    const handleRemoveConfig = (index) => {
        setConfigs(configs.filter((_, i) => i !== index));
    };

    const handleConfigChange = (index, field, value) => {
        const updatedConfigs = [...configs];
        updatedConfigs[index] = {
            ...configs[index],
            [field]: value
        };
        setConfigs(updatedConfigs);
    };

    // AutoTradeConfig.js
    const handleSave = () => {
        const configsToSave = configs.map(config => ({
            type: type,
            indicator: config.indicator,
            interval: config.interval,
            percentage: config.percentage || '',
            amount: config.amount || '',
            ccy: ccy
        }));

        onSave(configsToSave);
    };


    const ConfigItem = ({ config, index }) => (
    <Box className={classes.configItem}>
        <Box className={classes.fieldsContainer}>
            <TextField
                select
                label="指标"
                value={config.indicator || ''}
                onChange={(e) => handleConfigChange(index, 'indicator', e.target.value)}
                variant="outlined"
                size="small"
                style={{width: '120px'}}
            >
                {TRADE_INDICATORS.map(indicator => (
                    <MenuItem key={indicator.value} value={indicator.value}>
                        {indicator.label}
                    </MenuItem>
                ))}
            </TextField>

            <TextField
                label="指标值"
                defaultValue={config.interval || ''}
                onBlur={(e) => handleConfigChange(index, 'interval', e.target.value)}
                variant="outlined"
                size="small"
                type="number"
                style={{width: '100px'}}
                inputProps={{
                    step: "any"
                }}
            />

            <TextField
                label="金额"
                defaultValue={config.amount || ''}
                onBlur={(e) => handleConfigChange(index, 'amount', e.target.value)}
                variant="outlined"
                size="small"
                type="number"
                style={{width: '120px'}}
                inputProps={{
                    step: "any"
                }}
            />
        </Box>

        <Tooltip title="删除">
            <IconButton size="small" onClick={() => handleRemoveConfig(index)} style={{marginLeft: 'auto'}}>
                <DeleteIcon />
            </IconButton>
        </Tooltip>
    </Box>
);

    return (
        <>
            <DialogTitle disableTypography className={classes.dialogTitle}>
                <Box display="flex" alignItems="center">
                    <Typography variant="h6">
                        {ccy} - 自动{getTypeLabel()}配置
                    </Typography>
                    <Box
                        ml={2}
                        className={`${classes.typeIndicator} ${
                            type === 'stop_loss' 
                                ? classes.stopLossIndicator 
                                : classes.limitOrderIndicator
                        }`}
                    >
                        {getTypeLabel()}
                    </Box>
                </Box>
                <IconButton className={classes.closeButton} onClick={onClose}>
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent className={classes.content}>
                <Box>
                    {configs.map((config, index) => (
                        <ConfigItem
                            key={index}
                            config={config}
                            index={index}
                        />
                    ))}

                    <Button
                        variant="outlined"
                        startIcon={<AddIcon />}
                        onClick={handleAddConfig}
                        className={classes.addButton}
                        fullWidth
                    >
                        添加配置
                    </Button>
                </Box>
            </DialogContent>

            <Divider />

            <DialogActions>
                <Button onClick={onClose}>
                    取消
                </Button>
                <Button
                    onClick={handleSave}
                    color="primary"
                    variant="contained"
                >
                    保存
                </Button>
            </DialogActions>
        </>
    );
};