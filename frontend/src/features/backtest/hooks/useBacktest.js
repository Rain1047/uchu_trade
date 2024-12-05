import { useState, useEffect } from 'react';
import { fetchBacktestData } from '../utils/backtestAPI';

export const useBacktest = () => {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [backtestKeys, setBacktestKeys] = useState([]);
  const [selectedKey, setSelectedKey] = useState('');
  const [records, setRecords] = useState([]);
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [runningBacktest, setRunningBacktest] = useState(false);

  useEffect(() => {
    fetchSymbols();
  }, []);

  useEffect(() => {
    if (selectedSymbol) {
      fetchStrategies();
    }
  }, [selectedSymbol]);

  useEffect(() => {
    if (selectedSymbol && selectedStrategy) {
      fetchBacktestKeys();
    }
  }, [selectedSymbol, selectedStrategy]);

  useEffect(() => {
    if (selectedKey) {
      fetchRecordsAndDetails();
    }
  }, [selectedKey]);

  const fetchSymbols = async () => {
    try {
      const data = await fetchBacktestData.getSymbols();
      if (data.success) {
        setSymbols(data.data);
        if (data.data.length > 0) {
          setSelectedSymbol(data.data[0]);
        }
      }
    } catch (err) {
      setError('Failed to fetch symbols');
    }
  };

  const fetchStrategies = async () => {
    try {
      const data = await fetchBacktestData.getStrategies(selectedSymbol);
      if (data.success) {
        setStrategies(data.data);
        if (data.data.length > 0) {
          setSelectedStrategy(data.data[0].id);
        }
      }
    } catch (err) {
      setError('Failed to fetch strategies');
    }
  };

  const fetchBacktestKeys = async () => {
    try {
      const data = await fetchBacktestData.getKeys(selectedStrategy, selectedSymbol);
      if (data.success && data.data.length > 0) {
        setBacktestKeys(data.data);
        setSelectedKey(data.data[0]);
      }
    } catch (err) {
      setError('Failed to fetch backtest keys');
    }
  };

  const fetchRecordsAndDetails = async () => {
    setLoading(true);
    try {
      const [recordsData, detailsData] = await Promise.all([
        fetchBacktestData.getRecords(selectedKey),
        fetchBacktestData.getDetails(selectedKey)
      ]);

      if (recordsData.success) setRecords(recordsData.data);
      if (detailsData.success) setDetails(detailsData.data);
    } catch (err) {
      setError('Failed to fetch records and details');
    } finally {
      setLoading(false);
    }
  };

  const runBacktest = async () => {
    if (!selectedStrategy) return;

    setRunningBacktest(true);
    try {
      const result = await fetchBacktestData.runBacktest(selectedStrategy);
      if (result.success) {
        setSelectedKey(result.data.key);
        await fetchRecordsAndDetails();
      }
    } catch (error) {
      console.error('Run backtest failed:', error);
    } finally {
      setRunningBacktest(false);
    }
  };


  return {
    symbols,
    selectedSymbol,
    setSelectedSymbol,
    strategies,
    selectedStrategy,
    setSelectedStrategy,
    backtestKeys,
    selectedKey,
    setSelectedKey,
    records,
    details,
    loading,
    error,
    runBacktest,
    runningBacktest,
  };
};