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
  // 主输入框样式
  '& .MuiSelect-select': {
    color: '#fff', // 选中的文字颜色为白色
  },
  // 背景色
  backgroundColor: '#1E1E1E',
  // 边框样式
  '& .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  '&:hover .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    borderColor: '#2EE5AC',
  },
  // 图标颜色
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
    color: '#fff', // 输入文字为白色
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
});

export const AutoTradeConfig = ({ ccy, onClose, onSave }) => {
  const [activeType, setActiveType] = useState('limit');
  const [configs, setConfigs] = useState([{
    indicator: 'SMA',
    indicatorValue: '-1',
    percentage: '-1',
    amount: '1',
  }]);

  const handleTypeChange = (type) => {
    setActiveType(type);
  };

  const handleAddConfig = () => {
    setConfigs([...configs, {
      type: 'SMA',
      value: '-1',
      amount: '1',
      enabled: true
    }]);
  };

  // Menu Props for custom dropdown styling
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

  const handleRemoveConfig = (index) => {
    setConfigs(configs.filter((_, i) => i !== index));
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
          className={activeType === 'limit' ? 'active' : ''}
          onClick={() => handleTypeChange('limit')}
          sx={{ mr: 1 }}
        >
          限价
        </GreenButton>
        <GreenButton
          className={activeType === 'stop' ? 'active' : ''}
          onClick={() => handleTypeChange('stop')}
        >
          止损
        </GreenButton>
      </Box>

      {/* Config List */}
      <Box sx={{ p: 3 }}>
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
          }}
        >
          <FormControl sx={{ minWidth: 120 }}>
            <DarkInputLabel>指标</DarkInputLabel>
            <DarkSelect
              value={config.indicator}
              label="指标"
              MenuProps={menuProps}
            >
              <MenuItem value="SMA">SMA</MenuItem>
              <MenuItem value="EMA">EMA</MenuItem>
              <MenuItem value="USDT">USDT</MenuItem>
            </DarkSelect>
          </FormControl>

          <DarkTextField
            label="指标值"
            value={config.indicatorValue}
            type="number"
          />

          <DarkTextField
            label="百分比"
            value={config.percentage}
            type="number"
          />

          <DarkTextField
            label="数量"
            value={config.amount}
            type="number"
          />
        </Box>
      ))}
    </Box>

      {/* Add Config Button */}
      <GreenButton
        fullWidth
        startIcon={<AddIcon />}
        onClick={handleAddConfig}
        sx={{ mb: 3 }}
      >
        添加配置
      </GreenButton>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 'auto' }}>
        <GreenButton onClick={onClose}>
          取消
        </GreenButton>
        <GreenButton
          className="active"
          onClick={() => {
            onSave?.(configs);
            onClose();
          }}
        >
          保存
        </GreenButton>
      </Box>
    </Box>
  );
};