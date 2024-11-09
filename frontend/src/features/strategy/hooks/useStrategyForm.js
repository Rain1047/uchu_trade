import { useState, useEffect } from 'react';
import { validationRules } from '../constants/formValidation';
import {useStrategyApi} from './useStrategyApi';

export const useStrategyForm = (strategy = null) => {
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

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { createStrategy, updateStrategy } = useStrategyApi();

  useEffect(() => {
    if (strategy) {
      setFormData(prev => ({
        ...prev,
        ...strategy,
      }));
    }
  }, [strategy]);

  const validateForm = () => {
    const newErrors = {};
    Object.keys(validationRules).forEach(field => {
      const errorMessage = validationRules[field](formData[field]);
      if (errorMessage) {
        newErrors[field] = errorMessage;
      }
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return false;

    setLoading(true);
    try {
      if (strategy) {
        await updateStrategy(strategy.id, formData);
      } else {
        await createStrategy(formData);
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

  const handleChange = (field) => (event) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  return {
    formData,
    errors,
    loading,
    handleChange,
    handleSubmit,
    setFormData,
    validateForm
  };
};
