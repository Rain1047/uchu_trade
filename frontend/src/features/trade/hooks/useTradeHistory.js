import { useState, useEffect } from 'react';
import { INITIAL_FILTERS, MOCK_DATA } from '../constants/historyConstants';
import {fetchTradeHistory, updateTradeNote} from '../utils/api';

export const useTradeHistory = () => {
  const [tradeData, setTradeData] = useState({
    items: [],
    total_count: 0,
    page_size: 10,
    page_num: 1
  });
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [notes, setNotes] = useState({});

  useEffect(() => {
    fetchData();
  }, [filters.pageNum, filters.pageSize]);

  const fetchData = async () => {
    try {
      const data = await fetchTradeHistory(filters);
      if (!data.data?.items?.length) {
        setTradeData(MOCK_DATA);
        return;
      }
      setTradeData(data.data);
    } catch (error) {
      console.error('Error:', error);
      setTradeData(MOCK_DATA);
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePageChange = (newPage) => {
    setFilters(prev => ({
      ...prev,
      pageNum: newPage
    }));
  };

 const handleNoteChange = (id, value) => {
  setNotes(prev => ({
    ...prev,
    [id]: value
  }));
};

  const handleReset = () => {
    setFilters(INITIAL_FILTERS);
  };

  const handleNoteBlur = async (id, note) => {
     try {
       await updateTradeNote(id, note);
     } catch (error) {
       console.error('Failed to update note:', error);
     }
    };

  return {
    tradeData,
    filters,
    notes,
    handleFilterChange,
    handlePageChange,
    handleNoteChange,
    fetchData,
    handleReset,
    handleNoteBlur
  };
};