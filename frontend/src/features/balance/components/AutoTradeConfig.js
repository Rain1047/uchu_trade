// components/AutoTradeConfig.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Close as CloseIcon, Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// 自定义绿色主题按钮
const GreenButton = styled(Button)({
  color: '#2EE5AC',
  borderColor: '#2EE5AC',
  '&:hover': {
    borderColor: '#2EE5AC',
    backgroundColor: 'rgba(46, 229, 172, 0.08)',
  },
  '&.active': {
    backgroundColor: '#2EE5AC',
    color: '#000000',
    '&:hover': {
      backgroundColor: '#27CC98',
    },
  }
});

// 自定义深色主题下拉框
const DarkSelect = styled(Select)(({ theme }) => ({
  '& .MuiSelect-select': {
    color: '#fff',
  },
  backgroundColor: '#1E1E1E',
  '& .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  '&:hover .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    borderColor: '#2EE5AC',
  },
  '& .MuiSelect-icon': {
    color: '#fff',
  },
}));

// 自定义深色主题输入标签
const DarkInputLabel = styled(InputLabel)({
  color: 'rgba(255, 255, 255, 0.7)',
  '&.Mui-focused': {
    color: '#2EE5AC',
  },
});

// 自定义深色主题输入框
const DarkTextField = styled(TextField)({
  '& .MuiOutlinedInput-root': {
    color: '#fff',
    backgroundColor: '#1E1E1E',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.12)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#2EE5AC',
    },
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
    '&.Mui-focused': {
      color: '#2EE5AC',
    },
  },
  '&.Mui-disabled .MuiOutlinedInput-root': {
    color: 'rgba(255, 255, 255, 0.3)',
  },
});

export const AutoTradeConfig = ({ ccy, onClose, onSave }) => {
  const [activeType, setActiveType] = useState('limit');
  const [configs, setConfigs] = useState([{
    indicator: 'SMA',
    indicator_val: '-1',
    target_price: '',
    percentage: '',
    amount: '1',
    exec_nums: 1,
  }]);
  const [loading, setLoading] = useState(false);

  const menuProps = {
    PaperProps: {
      sx: {
        bgcolor: '#1E1E1E',
        '& .MuiMenuItem-root': {
          color: '#fff',
          '&:hover': {
            bgcolor: 'rgba(46, 229, 172, 0.08)',
          },
          '&.Mui-selected': {
            bgcolor: 'rgba(46, 229, 172, 0.16)',
            '&:hover': {
              bgcolor: 'rgba(46, 229, 172, 0.24)',
            },
          },
        },
      },
    },
  };

  const fetchConfigs = async (type) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/balance/list_configs/${ccy}/${type}?type_=${type}`);
      const result = await response.json();
      if (result.success) {
        setConfigs(result.data.filter(config => config.is_del === '0'));
      }
    } catch (error) {
      console.error('Failed to fetch configs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs(activeType);
  }, [activeType, ccy]);


  const handleTypeChange = (type) => {
    setActiveType(type);
  };

  const handleConfigChange = (index, field, value) => {
    const newConfigs = [...configs];
    const config = { ...newConfigs[index] };

    // 处理百分比和数量互斥
    if (field === 'percentage' && value) {
      config.amount = '';
    }
    if (field === 'amount' && value) {
      config.percentage = '';
    }

    config[field] = value;
    newConfigs[index] = config;
    setConfigs(newConfigs);
  };

  const handleAddConfig = () => {
    setConfigs([...configs, {
      ccy,
      type: activeType,
      indicator: 'SMA',
      indicator_val: null,
      target_price: null,
      percentage: null,
      amount: null,
      switch: '0',
      exec_nums: 1,
      is_del: '0'
    }]);
  };

  const handleRemoveConfig = (index) => {
    const newConfigs = [...configs];
    if (newConfigs[index].id) {
      newConfigs[index] = { ...newConfigs[index], is_del: '1' };
      setConfigs(newConfigs);
    } else {
      setConfigs(configs.filter((_, i) => i !== index));
    }
  };

  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6" sx={{ color: '#fff' }}>
          配置详情 - {ccy}
        </Typography>
        <IconButton onClick={onClose} sx={{ color: '#fff' }}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Type Toggle */}
      <Box sx={{ mb: 4 }}>
        <GreenButton
          className={activeType === 'limit_order' ? 'active' : ''}
          onClick={() => handleTypeChange('limit_order')}
          sx={{ mr: 1 }}
        >
          限价
        </GreenButton>
        <GreenButton
          className={activeType === 'stop_loss' ? 'active' : ''}
          onClick={() => handleTypeChange('stop_loss')}
        >
          止损
        </GreenButton>
      </Box>

      {/* Config List */}
      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        {configs.map((config, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              gap: 2,
              mb: 2,
              p: 2,
              bgcolor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: 1,
              alignItems: 'center',
            }}
          >
            <FormControl sx={{ minWidth: 120 }}>
              <DarkInputLabel>指标</DarkInputLabel>
              <DarkSelect
                value={config.indicator}
                label="指标"
                onChange={(e) => handleConfigChange(index, 'indicator', e.target.value)}
                MenuProps={menuProps}
              >
                <MenuItem value="SMA">SMA</MenuItem>
                <MenuItem value="EMA">EMA</MenuItem>
                <MenuItem value="USDT">USDT</MenuItem>
              </DarkSelect>
            </FormControl>

            <DarkTextField
              label={config.indicator === 'USDT' ? "目标价格" : "指标值"}
              value={(config.indicator === 'USDT' ? config.target_price : config.indicator_val) || ''}
              onChange={(e) => handleConfigChange(
                index,
                config.indicator === 'USDT' ? 'target_price' : 'indicator_val',
                e.target.value
              )}
              type="number"
              sx={{ width: 120 }}
            />

            <DarkTextField
              label="百分比"
              value={config.percentage || ''}
              onChange={(e) => handleConfigChange(index, 'percentage', e.target.value)}
              type="number"
              sx={{ width: 100 }}
              disabled={!!config.amount}
            />

            <DarkTextField
              label="数量"
              value={config.amount || ''}
              onChange={(e) => handleConfigChange(index, 'amount', e.target.value)}
              type="number"
              sx={{ width: 100 }}
              disabled={!!config.percentage}
            />

            <DarkTextField
              label="执行次数"
              value={config.exec_nums || 1}
              onChange={(e) => handleConfigChange(index, 'exec_nums', e.target.value)}
              type="number"
              sx={{ width: 100 }}
            />

            <IconButton
              onClick={() => handleRemoveConfig(index)}
              sx={{
                color: '#fff',
                '&:hover': {
                  color: '#ff4444',
                },
              }}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        ))}
      </Box>

      {/* Add Config Button */}
      <GreenButton
        fullWidth
        startIcon={<AddIcon />}
        onClick={handleAddConfig}
        sx={{ my: 3 }}
      >
        添加配置
      </GreenButton>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <GreenButton onClick={onClose}>
          取消
        </GreenButton>
        <GreenButton
          className="active"
          onClick={() => {
            onSave?.(configs.filter(config => config.is_del === '0'));
            onClose();
          }}
        >
          保存
        </GreenButton>
      </Box>
    </Box>
  );
};