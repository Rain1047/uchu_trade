import { useState, useCallback, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/balance';

export const useBalance = () => {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchBalance = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/list_balance`);
            const data = await response.json();
            if (data.success && data.data) {
                setAssets(data.data);
            } else {
                throw new Error(data.message || '获取数据失败');
            }
        } catch (err) {
            setError(err.message);
            console.error('Error fetching balance:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const saveAutoConfig = useCallback(async (ccy, type, configs) => {
        try {
            const response = await fetch(`${API_BASE}/auto_config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ccy, type, configs }),
            });

            if (response.ok) {
                await fetchBalance();
                return true;
            }
            return false;
        } catch (err) {
            console.error('Error saving config:', err);
            return false;
        }
    }, [fetchBalance]);

    // 只在组件挂载时获取一次数据
    useEffect(() => {
        fetchBalance();
    }, [fetchBalance]);

    return {
        assets,
        loading,
        error,
        fetchBalance,
        saveAutoConfig
    };
};