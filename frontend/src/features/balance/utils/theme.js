import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2EE5AC',
      light: '#27CC98',
      dark: '#25B989',
      contrastText: '#000000',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        containedPrimary: {
          backgroundColor: '#2EE5AC',
          color: '#000000',
          '&:hover': {
            backgroundColor: '#27CC98',
          },
        },
        outlinedPrimary: {
          color: '#2EE5AC',
          borderColor: '#2EE5AC',
          '&:hover': {
            borderColor: '#27CC98',
            backgroundColor: 'rgba(46, 229, 172, 0.08)',
          },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        switchBase: {
          '&.Mui-checked': {
            color: '#2EE5AC',
            '& + .MuiSwitch-track': {
              backgroundColor: '#2EE5AC',
            },
          },
        },
      },
    },
  },
});