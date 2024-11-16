import { useState, useEffect } from 'react';

export const useBalance = () => {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchBalance = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/balance');
            const data = await response.json();
            if (data.success && data.data) {
                setAssets(data.data);
            }
        } catch (err) {
            setError(err.message);
            console.error('Error fetching balance:', err);
        } finally {
            setLoading(false);
        }
    };

    const saveAutoConfig = async (ccy, type, configs) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/balance/auto_config', {
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
    };

    useEffect(() => {
        fetchBalance();
        const intervalId = setInterval(fetchBalance, 10000);
        return () => clearInterval(intervalId);
    }, []);

    return {
        assets,
        loading,
        error,
        fetchBalance,
        saveAutoConfig
    };
};