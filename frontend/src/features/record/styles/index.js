// features/record/styles/index.ts
import { styled } from '@mui/material/styles';
import {TextField, Button, TableContainer, Select, FormControl} from '@mui/material';
import {makeStyles} from "@material-ui/core/styles";

// 新增 FormControl 样式组件
export const DarkFormControl = styled(FormControl)(({ theme }) => ({
  width: '100%',
  minWidth: 'unset',
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
  width: '100%',
  minWidth: 'unset',
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
  backgroundColor: 'transparent',
  '& .MuiTableHead-root': {
    backgroundColor: '#1A1A1A',
    '& .MuiTableCell-head': {
      color: '#999',
      borderBottom: 'none',
      fontSize: '14px',
      padding: '16px',
    }
  },
  '& .MuiTableCell-root': {
    borderBottom: 'none',  // 移除所有边框
    padding: '16px',
    color: '#fff',
  },
  '& .MuiTableRow-root': {
    '&:nth-of-type(odd)': {
      backgroundColor: 'rgba(255, 255, 255, 0.02)',
    },
    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.04)',
    },
    height: '60px', // 统一行高
  },
});

// 表格容器的样式
export const tableStyles = {
  container: {
    padding: '16px 24px',
    p: 3,
    bgcolor: '#121212',
    minHeight: '100vh'
  },
  searchArea: {
    display: 'grid',
    gridTemplateColumns: '200px 150px 120px 120px 150px auto auto', // 对应表格列宽
    gap: '16px',
    alignItems: 'center',
    padding: '0 16px', // 与表格保持相同的内边距
    marginBottom: '20px'
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
      borderRadius: '4px',
      padding: '6px 12px',
      display: 'inline-block',
      fontSize: '12px',
      fontWeight: 500,
    },
    buy: {
      backgroundColor: '#198754',
      color: '#fff',
      borderRadius: '4px',
      padding: '6px 12px',
      display: 'inline-block',
      fontSize: '12px',
      fontWeight: 500,
    }
  },
  noteInput: {
    '& .MuiInput-input': {
      color: '#fff',
      fontSize: '14px',
    },
    '&:before': {
      borderBottomColor: 'rgba(255, 255, 255, 0.12)',
    },
    '&:hover:not(.Mui-disabled):before': {
      borderBottomColor: 'rgba(255, 255, 255, 0.2)',
    },
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
  },

}));
