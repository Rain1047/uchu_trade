// balance/index.js
import React, { useEffect } from 'react';
import { Container, Box, Alert } from '@mui/material';
import { BalanceHeader } from './components/BalanceHeader';
import { BalanceTable } from './components/BalanceTable';
import { useBalance } from './hooks/useBalance';

const BalanceManagement = () => {
  const {
    balances,
    loading,
    error,
    fetchBalances,
    updateSwitch,
    saveConfigs
  } = useBalance();

  useEffect(() => {
    fetchBalances();
  }, [fetchBalances]);

  const handleRefresh = async () => {
    await fetchBalances();
  };

  const handleSwitchToggle = async (ccy, type) => {
    const currentBalance = balances.find(b => b.ccy === ccy);
    const currentValue = type === 'stop_loss' ?
      currentBalance.stop_loss_switch === 'true' :
      currentBalance.limit_order_switch === 'true';

    await updateSwitch(ccy, type, !currentValue);
  };

  const handleConfigSave = async (configs) => {
    const success = await saveConfigs(configs);
    if (success) {
      await fetchBalances();
    }
    return success;
  };

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <BalanceHeader
          onRefresh={handleRefresh}
          refreshing={loading}
        />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <BalanceTable
          data={balances}
          onSwitchToggle={handleSwitchToggle}
          onConfigSave={handleConfigSave}
        />
      </Container>
    </Box>
  );
};

export default BalanceManagement;