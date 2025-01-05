// features/record/components/TradeRecordTable.js
import React, { useEffect, useState } from 'react';
import {
  Table,
  Select,
  Input,
  DatePicker,
  Space
} from '@mui/material';
import { TRADE_TYPES, TRADE_SIDES, EXEC_SOURCES, TIME_RANGES } from '../constants';
import { TradeRecord, TradeRecordQuery } from '../types';

export const TradeRecordTable = () => {
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState({
    pageNum: 1,
    pageSize: 10
  });

  const columns = [
    {
      title: '符号',
      dataIndex: 'ccy',
      key: 'ccy'
    },
    {
      title: '交易类别',
      dataIndex: 'type',
      key: 'type',
      render: (type) => TRADE_TYPES.find(t => t.value === type)?.label
    },
    {
      title: '交易方向',
      dataIndex: 'side',
      key: 'side',
      render: (side) => TRADE_SIDES.find(s => s.value === side)?.label
    },
    {
      title: '数量(USDT)',
      dataIndex: 'amount',
      key: 'amount'
    },
    {
      title: '交易价格',
      dataIndex: 'exec_price',
      key: 'exec_price'
    },
    {
      title: '交易方式',
      dataIndex: 'exec_source',
      key: 'exec_source',
      render: (source) => EXEC_SOURCES.find(s => s.value === source)?.label
    },
    {
      title: '交易时间',
      dataIndex: 'uTime',
      key: 'uTime'
    },
    {
      title: '交易日志',
      dataIndex: 'note',
      key: 'note'
    }
  ];

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/record/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query)
      });
      const data = await response.json();
      if (data.success) {
        setRecords(data.records);
        setTotal(data.total);
      }
    } catch (error) {
      console.error('Failed to fetch records:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [query]);

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索符号"
          onChange={e => setQuery(q => ({ ...q, ccy: e.target.value }))}
        />
        <Select
          mode="multiple"
          placeholder="交易类别"
          options={TRADE_TYPES}
          onChange={values => setQuery(q => ({ ...q, type: values }))}
        />
        <Select
          placeholder="交易方向"
          options={TRADE_SIDES}
          onChange={value => setQuery(q => ({ ...q, side: value }))}
        />
        <Select
          placeholder="交易方式"
          options={EXEC_SOURCES}
          onChange={value => setQuery(q => ({ ...q, exec_source: value }))}
        />
        <DatePicker.RangePicker
          onChange={(dates) => {
            if (dates) {
              setQuery(q => ({
                ...q,
                beginTime: dates[0]?.format('YYYY-MM-DD'),
                endTime: dates[1]?.format('YYYY-MM-DD')
              }));
            }
          }}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={records}
        loading={loading}
        pagination={{
          total,
          current: query.pageNum,
          pageSize: query.pageSize,
          onChange: (page, pageSize) =>
            setQuery(q => ({ ...q, pageNum: page, pageSize }))
        }}
      />
    </div>
  );
};