import { useState, useCallback } from 'react';

const API_ENDPOINTS = {
    LIST_BALANCE: 'http://127.0.0.1:8000/api/balance/list_balance',
    AUTO_CONFIG: 'http://127.0.0.1:8000/api/balance/auto_config',
    TOGGLE_SWITCH: 'http://127.0.0.1:8000/api/balance/toggle_switch'
};

export const useBalance = () => {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleApiResponse = async (response, errorMessage) => {
        if (!response.ok) {
            throw new Error(errorMessage);
        }
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || errorMessage);
        }
        return data;
    };

    const fetchBalance = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(API_ENDPOINTS.LIST_BALANCE);
            const data = await handleApiResponse(response, '获取资产数据失败');
            setAssets(data.data || []);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('获取资产列表失败:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const saveAutoConfig = useCallback(async (ccy, type, configs) => {
        try {
            const response = await fetch(API_ENDPOINTS.AUTO_CONFIG, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ccy, type, configs }),
            });
            await handleApiResponse(response, '保存配置失败');
            await fetchBalance();
            return true;
        } catch (err) {
            console.error('保存配置失败:', err);
            return false;
        }
    }, [fetchBalance]);

    const toggleAutoSwitch = useCallback(async (ccy, type, value) => {
        try {
            const response = await fetch(API_ENDPOINTS.TOGGLE_SWITCH, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ccy, type, value }),
            });
            await handleApiResponse(response, '切换开关失败');
            await fetchBalance();
            return true;
        } catch (err) {
            console.error('切换开关失败:', err);
            return false;
        }
    }, [fetchBalance]);

    return {
        assets,
        loading,
        error,
        fetchBalance,
        saveAutoConfig,
        toggleAutoSwitch
    };
};