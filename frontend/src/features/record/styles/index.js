// features/record/styles/index.ts
import { styled } from '@mui/material/styles';
import {TextField, Button, TableContainer, Select} from '@mui/material';
import {makeStyles} from "@material-ui/core/styles";

export const DarkSelect = styled(Select)(({ theme }) => ({
  backgroundColor: '#1E1E1E',
  color: '#fff',
  minWidth: '180px',
  '& .MuiOutlinedInput-root': {
    borderRadius: '4px',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.12)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.2)',
    },
  },
  '& .MuiSelect-select': {
    padding: '10px 14px',
    fontSize: '14px',
  },
  '& .MuiSelect-icon': {
    color: '#fff',
  }
}));


// 搜索区域样式
export const searchAreaStyles = {
  container: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 2,
    mb: 3,
  },
  selectGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 2,
    flex: 1,
    minWidth: '300px',
  },
  buttonGroup: {
    display: 'flex',
    gap: 2,
    alignItems: 'flex-start',
  }
};

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
  selectWrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(0.5),
  },

  selectLabel: {
    color: '#fff',
    fontSize: '14px',
    opacity: 0.7,
    paddingLeft: theme.spacing(0.5),
  },


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

export const useStyles = makeStyles((theme) => ({


  // 布局相关
  container: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
  },
  selectGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: theme.spacing(2),
    flex: 1,
    minWidth: '300px',
  },
  buttonGroup: {
    display: 'flex',
    gap: theme.spacing(2),
    alignItems: 'flex-start',
    '& > :not(:last-child)': {
      marginRight: theme.spacing(2),
    }
  },
  searchContainer: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: theme.spacing(2)
  },

  // 分页相关
  paginationContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: theme.spacing(2),
    gap: theme.spacing(2)
  },
  pageControl: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1)
  },

  // 交易方向标签
  buyChip: {
    backgroundColor: '#1b5e20',
    color: '#fff'
  },
  sellChip: {
    backgroundColor: '#b71c1c',
    color: '#fff'
  },

  // 输入框相关
  noteField: {
    minWidth: '200px',
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.23)',
      },
      '&:hover fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.4)',
      },
      '&.Mui-focused fieldset': {
        borderColor: '#2EE5AC',
      }
    },
    '& .MuiInputLabel-root': {
      color: 'rgba(255, 255, 255, 0.7)',
    },
    '& .MuiInputBase-input': {
      color: '#fff',
    }
  }
}));