import React from 'react';
import { Box, TextField, IconButton, Tooltip } from '@material-ui/core';
import { Delete as DeleteIcon } from '@material-ui/icons';

const ConfigItem = ({ config, index, handleConfigChange, handleRemoveConfig, classes }) => {
    const isUSDT = config.indicator === 'USDT'; // 判断是否为 USDT
    const disableAmount = !!config.percentage; // 填写百分比时禁用金额输入框
    const disablePercentage = !!config.amount; // 填写金额时禁用百分比输入框

    return (
        <Box className={classes.configItem}>
            {/* 指标下拉菜单 */}
            <TextField
                select
                label="指标"
                value={config.indicator || ''}
                onChange={(e) => handleConfigChange(index, 'indicator', e.target.value)}
                variant="outlined"
                size="small"
                style={{ width: '120px' }}
            >
                {/* 动态指标选项 */}
                {['USDT', 'EMA', 'SMA'].map(indicator => (
                    <option key={indicator} value={indicator}>
                        {indicator}
                    </option>
                ))}
            </TextField>

            {/* 指标值或目标价格 */}
            {isUSDT ? (
                <TextField
                    label="目标价格"
                    value={config.target_price || ''}
                    onChange={(e) => handleConfigChange(index, 'target_price', e.target.value)}
                    variant="outlined"
                    size="small"
                    type="number"
                    style={{ width: '120px' }}
                    inputProps={{
                        step: 'any',
                    }}
                />
            ) : (
                <TextField
                    label="指标值"
                    value={config.indicator_val || ''}
                    onChange={(e) => handleConfigChange(index, 'indicator_val', e.target.value)}
                    variant="outlined"
                    size="small"
                    type="number"
                    style={{ width: '100px' }}
                    inputProps={{
                        step: 'any',
                    }}
                />
            )}

            {/* 百分比 */}
            <TextField
                label="百分比"
                value={config.percentage || ''}
                onChange={(e) => handleConfigChange(index, 'percentage', e.target.value)}
                variant="outlined"
                size="small"
                type="number"
                style={{ width: '100px' }}
                inputProps={{
                    step: 'any',
                }}
                disabled={disablePercentage} // 禁用逻辑
            />

            {/* 金额 */}
            <TextField
                label="金额"
                value={config.amount || ''}
                onChange={(e) => handleConfigChange(index, 'amount', e.target.value)}
                variant="outlined"
                size="small"
                type="number"
                style={{ width: '120px' }}
                inputProps={{
                    step: 'any',
                }}
                disabled={disableAmount} // 禁用逻辑
            />

            {/* 执行次数 */}
            <TextField
                label="执行次数"
                value={config.exec_nums || '1'}
                onChange={(e) => handleConfigChange(index, 'exec_nums', e.target.value)}
                variant="outlined"
                size="small"
                type="number"
                style={{ width: '100px' }}
            />

            {/* 删除按钮 */}
            <Tooltip title="删除">
                <IconButton
                    size="small"
                    onClick={() => handleRemoveConfig(index)}
                    style={{ marginLeft: 'auto' }}
                >
                    <DeleteIcon />
                </IconButton>
            </Tooltip>
        </Box>
    );
};

export default ConfigItem;
