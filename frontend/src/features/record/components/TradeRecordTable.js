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
  InputLabel,
  CircularProgress,
  Box,
  Pagination,
  IconButton,
} from '@mui/material';
import {TRADE_TYPES, TRADE_SIDES, EXEC_SOURCES, TIME_RANGES, TRADE_STATUS} from '../constants/constants';
import {
  useStyles,
  DarkTextField,
  DarkSelect,
  SearchButton,
  ResetButton,
  StyledTableContainer,
  tableStyles,
  DarkFormControl,
} from '../styles';
import {INITIAL_FILTERS} from "../../trade/constants/historyConstants";
import {Button, Typography} from "@material-ui/core";
import {Refresh as RefreshIcon, Clear as ClearIcon} from "@material-ui/icons";

const TradeRecordTable = () => {
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [query, setQuery] = useState({
    pageNum: 1,
    pageSize: 10,
    ccy: '',
    type: '',
    side: '',
    exec_source: '',
    begin_time: '',
    end_time: '',
    timeRange: '',
  });

  const handleReset = () => {
    setQuery({
      ...query,
      ccy: '',
      type: '',
      side: '',
      exec_source: '',
      begin_time: '',
      end_time: '',
      timeRange: '',
    });
  };

  const classes = useStyles();

  const menuProps = {
    classes: { paper: classes.selectMenu },
    MenuListProps: {
      sx: { backgroundColor: '#1E1E1E' }
    },
    PaperProps: {
      sx: { backgroundColor: '#1E1E1E' }
    },
    anchorOrigin: {
      vertical: 'bottom',
      horizontal: 'left',
    },
    transformOrigin: {
      vertical: 'top',
      horizontal: 'left',
    },
  };

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

  const updateQuery = (key, value) => {
    setQuery((prev) => ({ ...prev, [key]: value }));
  };

  const handleClearSelect = (field) => {
    updateQuery(field, '');
    if (field === 'timeRange') {
      updateQuery('begin_time', '');
      updateQuery('end_time', '');
    }
  };

  const renderSelectValue = (selected, placeholder, options) => {
    if (!selected) {
      return <span style={{ color: 'rgba(255, 255, 255, 0.5)' }}>{placeholder}</span>;
    }
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        <span>{options.find(item => item.value === selected)?.label}</span>
        <IconButton
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            handleClearSelect(placeholder === '时间范围' ? 'timeRange' : placeholder === '交易类别' ? 'type' : placeholder === '交易方向' ? 'side' : 'exec_source');
          }}
          sx={{ color: 'rgba(255, 255, 255, 0.5)' }}
        >
          <ClearIcon fontSize="small" />
        </IconButton>
      </Box>
    );
  };

  return (
    <Box sx={tableStyles.container}>
      <Typography
        variant="h5"
        component="h2"
        style={{
          margin: '0 0 20px 0',  // 移除上边距，只保留下边距
          color: '#fff'
        }}
      >
        Trade History
      </Typography>

      <Box sx={tableStyles.searchArea}>
        <DarkFormControl>
          <DarkTextField
            placeholder="交易符号"
            size="small"
            value={query.ccy}
            onChange={(e) => updateQuery('ccy', e.target.value)}
            InputProps={{
              endAdornment: query.ccy && (
                <IconButton
                  size="small"
                  onClick={() => updateQuery('ccy', '')}
                  sx={{ color: 'rgba(255, 255, 255, 0.5)' }}
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              ),
            }}
          />
        </DarkFormControl>

        <DarkSelect
          value={query.type}
          onChange={(e) => updateQuery('type', e.target.value)}
          MenuProps={menuProps}
          displayEmpty
          renderValue={(selected) => renderSelectValue(selected, '交易类别', TRADE_TYPES)}
        >
          <MenuItem value="">全部</MenuItem>
          {TRADE_TYPES.map((type) => (
            <MenuItem key={type.value} value={type.value}>
              {type.label}
            </MenuItem>
          ))}
        </DarkSelect>

        <DarkSelect
          value={query.side}
          onChange={(e) => updateQuery('side', e.target.value)}
          MenuProps={menuProps}
          displayEmpty
          renderValue={(selected) => renderSelectValue(selected, '交易方向', TRADE_SIDES)}
        >
          <MenuItem value="">全部</MenuItem>
          {TRADE_SIDES.map((side) => (
            <MenuItem key={side.value} value={side.value}>
              {side.label}
            </MenuItem>
          ))}
        </DarkSelect>

        <DarkSelect
          value={query.exec_source}
          onChange={(e) => updateQuery('exec_source', e.target.value)}
          MenuProps={menuProps}
          displayEmpty
          renderValue={(selected) => renderSelectValue(selected, '交易方式', EXEC_SOURCES)}
        >
          <MenuItem value="">全部</MenuItem>
          {EXEC_SOURCES.map((source) => (
            <MenuItem key={source.value} value={source.value}>
              {source.label}
            </MenuItem>
          ))}
        </DarkSelect>

        <DarkSelect
          value={query.timeRange}
          onChange={(e) => {
            const days = e.target.value;
            if (days) {
              const endDate = new Date();
              const startDate = new Date();
              startDate.setDate(startDate.getDate() - days);
              updateQuery('begin_time', startDate.toISOString().split('T')[0]);
              updateQuery('end_time', endDate.toISOString().split('T')[0]);
              updateQuery('timeRange', days);
            }
          }}
          MenuProps={menuProps}
          displayEmpty
          renderValue={(selected) => renderSelectValue(selected, '时间范围', TIME_RANGES)}
        >
          <MenuItem value="">选择时间范围</MenuItem>
          {TIME_RANGES.map((range) => (
            <MenuItem key={range.value} value={range.value}>
              {range.label}
            </MenuItem>
          ))}
        </DarkSelect>

        <SearchButton variant="contained" onClick={fetchRecords}>
          查询
        </SearchButton>
        <ResetButton variant="contained" onClick={handleReset}>
          重置
        </ResetButton>
      </Box>

      <StyledTableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>交易类别</TableCell>
              <TableCell>交易方向</TableCell>
              <TableCell>交易数量/USDT</TableCell>
              <TableCell>成交价格</TableCell>
              <TableCell>交易来源</TableCell>
              <TableCell>订单状态</TableCell>
              <TableCell>成交时间</TableCell>
              <TableCell>交易日志</TableCell>
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
                <TableCell>{record.ccy}</TableCell>
                <TableCell>
                  {TRADE_TYPES.find(type => type.value === record.type)?.label || record.type}
                </TableCell>
                <TableCell>
                  <Box sx={tableStyles.sideTag[record.side]}>
                    {TRADE_SIDES.find(side => side.value === record.side)?.label || record.side}
                  </Box>
                </TableCell>
                <TableCell>{record.amount}</TableCell>
                <TableCell>{record.exec_price}</TableCell>
                <TableCell>
                  {EXEC_SOURCES.find(exec_source => exec_source.value === record.exec_source)
                      ?.label || record.exec_source}
                </TableCell>
                <TableCell>
                  {TRADE_STATUS.find(status => status.value === record.status)?.label || record.status}
                </TableCell>
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