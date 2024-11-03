import { createTheme } from '@material-ui/core/styles';

export const darkTheme = createTheme({
  palette: {
    type: 'dark',
    background: {
      default: '#131313',
      paper: '#222',
    },
    text: {
      primary: '#fff',
      secondary: '#888',
    },
    primary: {
      main: '#5eddac',
    },
    secondary: {
      main: '#f57ad0',
    },
  },
  overrides: {
    MuiContainer: {
      root: {
        backgroundColor: '#131313',
        minHeight: '100vh',
        padding: 24,
      },
    },
    MuiCard: {
      root: {
        backgroundColor: '#222',
        border: '1px solid #444',
        marginBottom: 24,
      },
    },
    MuiInputBase: {
      input: {
        color: '#fff',
      },
    },
    MuiOutlinedInput: {
      root: {
        '& fieldset': {
          borderColor: '#444',
        },
        '&:hover fieldset': {
          borderColor: '#666',
        },
      },
    },
    MuiInputLabel: {
      root: {
        color: '#888',
      },
    },
    MuiTableCell: {
      head: {
        backgroundColor: '#1a1a1a',
        color: '#888',
        borderBottom: '1px solid #444',
      },
      body: {
        color: '#fff',
        borderBottom: '1px solid #444',
      },
    },
    MuiChip: {
      root: {
        '&.buyChip': {
          backgroundColor: '#5eddac',
          color: '#000',
        },
        '&.sellChip': {
          backgroundColor: '#f57ad0',
          color: '#000',
        },
      },
    },
    MuiPaper: {
      root: {
        backgroundColor: '#222',
      },
    },
    MuiButton: {
      root: {
        backgroundColor: '#222',
        color: '#fff',
        borderColor: '#444',
        '&:hover': {
          backgroundColor: '#2a2a2a',
        },
        '&.Mui-disabled': {
          color: '#666',
          borderColor: '#333',
        },
      },
    },
    MuiSelect: {
      root: {
        backgroundColor: '#131313',
        color: '#fff',
        '& .MuiSelect-icon': {
          color: '#fff',
        },
      },
    },
  },
});