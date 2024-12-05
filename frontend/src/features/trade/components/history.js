import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Box,
  Select,
  MenuItem,
  IconButton,
  Chip
} from '@material-ui/core';
import {
  ArrowForward as ArrowForwardIcon,
  ArrowBack as ArrowBackIcon
} from '@material-ui/icons';
import { useStyles } from '../utils/styles';
import { useTradeHistory } from '../hooks/useTradeHistory';
import { SearchFilters } from './SearchFilters';
import { formatTimestamp, calculateAmount } from '../utils/helpers';
import {updateTradeNote} from "../utils/api";

function TradeHistoryTable() {
  const classes = useStyles();
  const {
    tradeData,
    filters,
    notes,
    handleFilterChange,
    handlePageChange,
    handleNoteChange,
    fetchData,
    handleReset
  } = useTradeHistory();

  const getSideChipStyle = (side) => {
    return side.toLowerCase() === 'buy' ? classes.buyChip : classes.sellChip;
  };

  const handleNoteBlur = async (id, note) => {
   try {
     await updateTradeNote(id, note);
   } catch (error) {
     console.error('Failed to update note:', error);
   }
  };

  return (
    <Container>
      <Typography variant="h5" gutterBottom>交易历史</Typography>

      <Card>
        <CardContent>
          <SearchFilters
            filters={filters}
            onChange={handleFilterChange}
            onSearch={fetchData}
            onReset={handleReset}
          />
        </CardContent>
      </Card>

      <Paper>
        <TableContainer>
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
              {tradeData.items.map((row) => (
                <TableRow key={row.trade_id} hover>
                  <TableCell>{row.trade_id}</TableCell>
                  <TableCell>{row.inst_id}</TableCell>
                  <TableCell>
                    <Chip
                      label={row.side?.toUpperCase()}
                      size="small"
                      className={getSideChipStyle(row.side)}
                    />
                  </TableCell>
                  <TableCell>{row.fill_px}</TableCell>
                  <TableCell>{calculateAmount(row.fill_px, row.fill_sz, row.fee)}</TableCell>
                  <TableCell>{formatTimestamp(row.fill_time)}</TableCell>
                  <TableCell>
                    <TextField
                     size="small"
                     variant="outlined"
                     value={notes[row.id] ?? row.note ?? ''}
                     onChange={(e) => handleNoteChange(row.id, e.target.value)}
                     onBlur={() => handleNoteBlur(row.id, notes[row.id])}
                     placeholder="Add note..."
                     multiline
                     maxRows={4}
                     className={classes.noteField}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box className={classes.paginationContainer}>
          <Select
            value={filters.pageSize}
            onChange={(e) => handleFilterChange({
              target: { name: 'pageSize', value: e.target.value }
            })}
            variant="outlined"
          >
            {[5, 10, 20, 50].map(size => (
              <MenuItem key={size} value={size}>{size} per page</MenuItem>
            ))}
          </Select>

          <Box className={classes.pageControl}>
            <IconButton
              onClick={() => handlePageChange(filters.pageNum - 1)}
              disabled={filters.pageNum === 1}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="body2">
              Page {filters.pageNum} of {Math.ceil(tradeData.total_count / filters.pageSize)}
            </Typography>
            <IconButton
              onClick={() => handlePageChange(filters.pageNum + 1)}
              disabled={filters.pageNum >= Math.ceil(tradeData.total_count / filters.pageSize)}
            >
              <ArrowForwardIcon />
            </IconButton>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default TradeHistoryTable;