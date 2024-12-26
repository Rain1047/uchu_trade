import { useState, useCallback } from 'react';
import { API_ENDPOINTS } from '../constants/balanceConstants';

export const useBalance = () => {
    const [balances, setBalances] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleApiResponse = async (response, errorMsg) => {
        if (!response.ok) {
            throw new Error(errorMsg);
        }
        const data = await response.json();
        if (!data.success && !data.data) {
            throw new Error(data.message || errorMsg);
        }
        return data;
    };

    const fetchBalances = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(API_ENDPOINTS.LIST_BALANCE);
            const { data } = await handleApiResponse(response, '获取资产数据失败');
            setBalances(data || []);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('获取资产列表失败:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const toggleAutoConfig = useCallback(async (ccy, type, enabled) => {
        try {
            const response = await fetch(API_ENDPOINTS.TOGGLE_SWITCH, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ccy, type, enabled }),
            });
            await handleApiResponse(response, '切换配置失败');
            await fetchBalances();
            return true;
        } catch (err) {
            console.error('切换配置失败:', err);
            return false;
        }
    }, [fetchBalances]);

    const saveAutoConfig = useCallback(async (ccy, type, configs) => {
        try {
            const response = await fetch(API_ENDPOINTS.AUTO_CONFIG, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ccy, type, configs }),
            });
            await handleApiResponse(response, '保存配置失败');
            await fetchBalances();
            return true;
        } catch (err) {
            console.error('保存配置失败:', err);
            return false;
        }
    }, [fetchBalances]);

    const saveTradeConfig = async (ccy, type, configs) => {
        try {
            const response = await fetch('/api/balance/save_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configs.map(config => ({
                    ...config,
                    ccy,
                    type
                })))
            });
            const data = await response.json();
            return data.success;
        } catch (error) {
            console.error('Save config failed:', error);
            return false;
        }
    };

    const fetchTradeConfigs = async (ccy, type) => {
        try {
            const response = await fetch(`/api/balance/list_configs/${ccy}/${type}`);
            const data = await response.json();
            return data.success ? data.data : [];
        } catch (error) {
            console.error('Fetch configs failed:', error);
            return [];
        }
    };


    return {
        balances,
        loading,
        error,
        fetchBalances,
        toggleAutoConfig,
        saveAutoConfig,
        saveTradeConfig,
        fetchTradeConfigs
    };
};