// features/record/styles/index.ts
import { makeStyles } from '@material-ui/core/styles';
import { styled } from '@mui/material/styles';
import { Select } from '@mui/material';

// Styled Components
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

// MakeStyles
export const useStyles = makeStyles((theme) => ({
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

// 移除独立的 searchAreaStyles，将其整合到 useStyles 中