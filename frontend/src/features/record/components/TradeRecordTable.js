import React, { useState, useEffect } from 'react';
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
  Box,
  Button,
  TableContainer,
  Paper,
  Pagination,
} from '@mui/material';
import { TRADE_TYPES, TRADE_SIDES, EXEC_SOURCES } from '../constants/constants';
import {
  DarkTextField,
  SearchButton,
  ResetButton,
  StyledTableContainer,
  tableStyles
} from '../styles';
const TradeRecordTable = () => {
  const [records, setRecords] = useState([]); // 交易记录数据
  const [total, setTotal] = useState(0); // 总记录数
  const [loading, setLoading] = useState(false); // 加载状态
  const [query, setQuery] = useState({
    pageNum: 1,
    pageSize: 10,
    ccy: '',
    type: '',
    side: '',
    exec_source: '',
    begin_time: '',
    end_time: '',
  });


  // 列定义
  const columns = [
    { label: '符号', key: 'ccy' },
    { label: '交易类别', key: 'type', render: (value) => TRADE_TYPES.find((t) => t.value === value)?.label },
    { label: '交易方向', key: 'side', render: (value) => TRADE_SIDES.find((t) => t.value === value)?.label },
    { label: '数量(USDT)', key: 'amount' },
    { label: '交易价格', key: 'exec_price' },
    { label: '交易方式', key: 'exec_source', render: (value) => EXEC_SOURCES.find((t) => t.value === value)?.label },
    { label: '交易时间', key: 'create_time' },
  ];

  // 请求数据
  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/record/list_spot_record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      });
      const data = await response.json();
      if (data.success) {
        setRecords(data.records || []);
        setTotal(data.total || 0);
      } else {
        console.error('Failed to fetch data:', data.message);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [query]);

  // 更新查询条件
  const updateQuery = (key, value) => {
    setQuery((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <Box sx={tableStyles.container}>
      {/* 搜索区域 */}
      <Box sx={tableStyles.searchArea}>
        <DarkTextField
          placeholder="Instrument ID"
          size="small"
          value={query.ccy}
          onChange={(e) => updateQuery('ccy', e.target.value)}
          sx={tableStyles.textField}
        />
        <DarkTextField
          label="Start Time"
          type="date"
          size="small"
          InputLabelProps={{ shrink: true }}
          value={query.begin_time}
          onChange={(e) => updateQuery('begin_time', e.target.value)}
        />
        <DarkTextField
          label="End Time"
          type="date"
          size="small"
          InputLabelProps={{ shrink: true }}
          value={query.end_time}
          onChange={(e) => updateQuery('end_time', e.target.value)}
        />
        <SearchButton variant="contained" onClick={fetchRecords}>
          SEARCH
        </SearchButton>
        {/*<ResetButton variant="contained" onClick={handleReset}>*/}
        {/*  RESET*/}
        {/*</ResetButton>*/}
      </Box>

      {/* 表格内容 */}
      <StyledTableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Trade ID</TableCell>
              <TableCell>Instrument</TableCell>
              <TableCell>Side</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Note</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <CircularProgress sx={{ color: '#2EE5AC' }} />
                </TableCell>
              </TableRow>
            ) : records.map((record) => (
              <TableRow key={record.id}>
                <TableCell>{record.id}</TableCell>
                <TableCell>{record.ccy}</TableCell>
                <TableCell>
                  <Box sx={tableStyles.sideTag[record.side]}>
                    {record.side.toUpperCase()}
                  </Box>
                </TableCell>
                <TableCell>{record.exec_price}</TableCell>
                <TableCell>{record.amount}</TableCell>
                <TableCell>{record.uTime}</TableCell>
                <TableCell>
                  <DarkTextField
                    placeholder="Add note..."
                    size="small"
                    variant="standard"
                    sx={tableStyles.noteInput}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </StyledTableContainer>

      {/* 分页 */}
      <Box sx={tableStyles.pagination}>
        <Pagination
          count={Math.ceil(total / query.pageSize)}
          page={query.pageNum}
          onChange={(event, page) => updateQuery('pageNum', page)}
        />
      </Box>
    </Box>
  );
};

export default TradeRecordTable;