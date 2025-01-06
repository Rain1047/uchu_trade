// features/record/styles/index.ts
import { styled } from '@mui/material/styles';
import {TextField, Button, TableContainer, Select, FormControl} from '@mui/material';
import {makeStyles} from "@material-ui/core/styles";

// 新增 FormControl 样式组件
export const DarkFormControl = styled(FormControl)(({ theme }) => ({
  minWidth: '180px',
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
    '&.Mui-focused': {
      color: '#2EE5AC',
    }
  },
  '& .MuiInputLabel-shrink': {
    transform: 'translate(0, -1.5px) scale(0.85)',
    color: 'rgba(255, 255, 255, 0.7)',
  }
}));

export const DarkSelect = styled(Select)(({ theme }) => ({
  backgroundColor: '#1E1E1E',
  color: '#fff',
  minWidth: '180px',
  '& .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  '&:hover .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    borderColor: '#2EE5AC',
  },
  '& .MuiSelect-select': {
    padding: '10px 14px',
    fontSize: '14px',
    backgroundColor: '#1E1E1E',
    color: '#fff',
  },
  '& .MuiSelect-icon': {
    color: '#fff',
  },
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

// 更新 TextField 组件样式
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
    '&.Mui-focused fieldset': {
      borderColor: '#2EE5AC',
    }
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
    '&.Mui-focused': {
      color: '#2EE5AC',
    }
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
      '&:hover': {
        backgroundColor: 'rgba(46, 229, 172, 0.08)',
      }
    },
    '& .Mui-selected': {
      backgroundColor: '#2EE5AC',
      color: '#000',
      '&:hover': {
        backgroundColor: '#27CC98',
      }
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

  // 更新下拉菜单样式
  selectMenu: {
    backgroundColor: '#1E1E1E',
    '& .MuiPaper-root': {
      backgroundColor: '#1E1E1E',
      color: '#fff',
      border: '1px solid rgba(255, 255, 255, 0.12)',
    },
    '& .MuiMenuItem-root': {
      color: '#fff',
      '&:hover': {
        backgroundColor: 'rgba(46, 229, 172, 0.08)',
      },
      '&.Mui-selected': {
        backgroundColor: 'rgba(46, 229, 172, 0.16)',
        '&:hover': {
          backgroundColor: 'rgba(46, 229, 172, 0.24)',
        }
      },
    },
  },

  pagination: {
    '& .MuiPaginationItem-root': {
      color: '#fff',
      '&:hover': {
        backgroundColor: 'rgba(46, 229, 172, 0.08)',
      }
    },
    '& .Mui-selected': {
      backgroundColor: '#2EE5AC',
      color: '#000',
      '&:hover': {
        backgroundColor: '#27CC98',
      },
    },
  },


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