// features/record/styles/index.ts
import { styled } from '@mui/material/styles';
import { TextField, Button, TableContainer } from '@mui/material';

export const DarkTextField = styled(TextField)({
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#1E1E1E',
    color: '#fff',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.12)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.2)',
    },
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
});

export const SearchButton = styled(Button)({
  backgroundColor: '#2EE5AC',
  color: '#000',
  '&:hover': {
    backgroundColor: '#27CC98',
  },
});

export const ResetButton = styled(Button)({
  backgroundColor: '#2A2A2A',
  color: '#fff',
  '&:hover': {
    backgroundColor: '#3A3A3A',
  },
});

export const StyledTableContainer = styled(TableContainer)({
  backgroundColor: '#1E1E1E',
  '& .MuiTableHead-root': {
    backgroundColor: '#2A2A2A',
  },
  '& .MuiTableCell-root': {
    borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
    color: '#fff',
  },
  '& .MuiTableRow-root:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.04)',
  },
});

// 表格容器的样式
export const tableStyles = {
  container: {
    p: 3,
    bgcolor: '#121212',
    minHeight: '100vh'
  },
  searchArea: {
    display: 'flex',
    gap: 2,
    mb: 3,
    alignItems: 'center'
  },
  textField: {
    width: 200
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    mt: 2,
    '& .MuiPaginationItem-root': {
      color: '#fff',
    },
    '& .Mui-selected': {
      backgroundColor: '#2EE5AC',
      color: '#000',
    },
  },
  sideTag: {
    sell: {
      backgroundColor: '#DC3545',
      color: '#fff',
      borderRadius: 1,
      px: 1,
      py: 0.5,
      display: 'inline-block',
    },
    buy: {
      backgroundColor: '#198754',
      color: '#fff',
      borderRadius: 1,
      px: 1,
      py: 0.5,
      display: 'inline-block',
    }
  },
  noteInput: {
    '& .MuiInput-input': {
      color: '#fff',
    }
  }
};