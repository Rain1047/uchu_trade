import React, { useState } from 'react';
import StrategyList from './components/StrategyList';
import StrategyForm from './components/StrategyForm';

const StrategyPage = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [viewMode, setViewMode] = useState(false);

  const handleAdd = () => {
    setSelectedStrategy(null);
    setViewMode(false);
    setDrawerOpen(true);
  };

  const handleEdit = (strategy) => {
    setSelectedStrategy(strategy);
    setViewMode(false);
    setDrawerOpen(true);
  };

  const handleView = (strategy) => {
    setSelectedStrategy(strategy);
    setViewMode(true);
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setSelectedStrategy(null);
    setViewMode(false);
  };

  return (
    <>
      <StrategyList 
        onAdd={handleAdd}
        onEdit={handleEdit}
        onView={handleView}
      />
      <StrategyForm
        open={drawerOpen}
        onClose={handleDrawerClose}
        strategy={selectedStrategy}
        viewMode={viewMode}
      />
    </>
  );
};

export default StrategyPage;
