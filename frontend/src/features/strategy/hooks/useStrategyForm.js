import { useState, useEffect } from 'react';
import { validationRules } from '../constants/formValidation';
import { useStrategyApi } from './useStrategyApi';

export const useStrategyForm = (strategy = null) => {
  // 基础表单数据
  const [formData, setFormData] = useState({
    name: '',
    trade_pair: '',
    time_frame: '',
    side: '',
    entry_per_trans: '',
    loss_per_trans: '',
    entry_st_code: '',
    exit_st_code: '',
    filter_st_code: '',
    schedule_config: {
      date: '',
      time: ''
    }
  });

  // 额外的表单状态
  const [stopLossConditions, setStopLossConditions] = useState([]);
  const [selectedDays, setSelectedDays] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const { createStrategy, updateStrategy } = useStrategyApi();

  // 加载现有数据
  useEffect(() => {
    if (strategy) {
      setFormData(prev => ({
        ...prev,
        ...strategy,
      }));

      // 加载止损配置
      if (strategy.stop_loss_config) {
        const stopLossArray = Object.entries(strategy.stop_loss_config).map(([type, value]) => ({
          type,
          value
        }));
        setStopLossConditions(stopLossArray);
      }

      // 加载调度配置
      if (strategy.schedule_config?.date) {
        setSelectedDays(strategy.schedule_config.date.split(',').map(Number));
      }
    }
  }, [strategy]);

  // 验证表单
  const validateForm = () => {
    const newErrors = {};

    // 基础字段验证
    Object.keys(validationRules).forEach(field => {
      const errorMessage = validationRules[field](formData[field]);
      if (errorMessage) {
        newErrors[field] = errorMessage;
      }
    });

    // 止损条件验证
    stopLossConditions.forEach((condition, index) => {
      if (!condition.type) {
        newErrors[`stopLoss_${index}_type`] = '请选择止损类型';
      }
      if (!condition.value) {
        newErrors[`stopLoss_${index}_value`] = '请输入止损值';
      }
    });

    // 调度配置验证
    if (selectedDays.length === 0) {
      newErrors.schedule_days = '请选择运行天数';
    }
    if (!formData.schedule_config.time) {
      newErrors.schedule_time = '请输入运行时间';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 提交表单
  const handleSubmit = async () => {
    if (!validateForm()) return false;

    setLoading(true);
    try {
      // 准备提交数据
      const submitData = {
        ...formData,
        stop_loss_config: stopLossConditions.reduce((acc, condition) => {
          if (condition.type && condition.value) {
            acc[condition.type] = condition.value;
          }
          return acc;
        }, {}),
        schedule_config: {
          date: selectedDays.join(','),
          time: formData.schedule_config.time
        }
      };

      if (strategy) {
        await updateStrategy(strategy.id, submitData);
      } else {
        await createStrategy(submitData);
      }
      return true;
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        submit: error.message
      }));
      return false;
    } finally {
      setLoading(false);
    }
  };

  // 处理表单字段变化
  const handleChange = (field) => (event) => {
    const value = event.target.value;
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // 止损条件处理函数
  const handleStopLossAdd = () => {
    setStopLossConditions(prev => [...prev, { type: '', value: '' }]);
  };

  const handleStopLossRemove = (index) => {
    setStopLossConditions(prev => prev.filter((_, i) => i !== index));
  };

  const handleStopLossChange = (index, field, value) => {
    setStopLossConditions(prev => prev.map((item, i) =>
      i === index ? { ...item, [field]: value } : item
    ));
  };

  // 处理星期选择
  const handleDayToggle = (day) => {
    setSelectedDays(prev => {
      const currentIndex = prev.indexOf(day);
      if (currentIndex === -1) {
        return [...prev, day].sort((a, b) => a - b);
      }
      return prev.filter(d => d !== day);
    });
  };

  return {
    formData,
    stopLossConditions,
    selectedDays,
    errors,
    loading,
    handleChange,
    handleStopLossAdd,
    handleStopLossRemove,
    handleStopLossChange,
    handleDayToggle,
    handleSubmit,
    setFormData,
    validateForm
  };
};