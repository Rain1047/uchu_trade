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


    const saveTradeConfig = useCallback(async (ccy, type, configs) => {
        try {
            const response = await fetch(API_ENDPOINTS.SAVE_CONFIG, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configs.map(config => ({
                    ...config,
                    ccy,
                    type
                })))
            });
            const { success, data, message } = await response.json();
            if (!success) {
                throw new Error(message || '保存配置失败');
            }
            await fetchBalances();
            return true;
        } catch (error) {
            console.error('保存配置失败:', error);
            return false;
        }
    }, [fetchBalances]);


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
        saveTradeConfig,
        fetchTradeConfigs
    };
};