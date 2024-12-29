import React from 'react';
import { Box, Typography, Button, CircularProgress } from '@material-ui/core';
import { Refresh as RefreshIcon } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import { styled } from '@mui/material/styles';

const GreenButton = styled(Button)({
  backgroundColor: '#2EE5AC',
  color: '#000000',
  '&:hover': {
    backgroundColor: '#27CC98',
  },
  '&:disabled': {
    backgroundColor: '#2EE5AC',
    opacity: 0.6,
  },
});

const useStyles = makeStyles((theme) => ({
   header: {
       display: 'flex',
       justifyContent: 'space-between',
       alignItems: 'center',
       marginBottom: theme.spacing(3),
       width: '100%',
       paddingLeft: theme.spacing(3),
       paddingRight: theme.spacing(4)
   }
}));

export const BalanceHeader = ({ onRefresh, refreshing }) => {
    const classes = useStyles();

    return (
       <Box className={classes.header} width="100%">
           <Box>
               <Typography variant="h5" align="left">资产管理</Typography>
           </Box>
           <Box display="flex" justifyContent="flex-end">
               <Button
                   variant="contained"
                   color="primary"
                   onClick={onRefresh}
                   disabled={refreshing}
                   endIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
               >
                   刷新
               </Button>
           </Box>
       </Box>
   );
};


// export const BalanceHeader = ({ onRefresh, refreshing }) => {
//   return (
//     <Box
//       sx={{
//         display: 'flex',
//         justifyContent: 'space-between',
//         alignItems: 'center',
//         mb: 3,
//         px: 3
//       }}
//     >
//       <Typography variant="h5" sx={{ color: 'common.white' }} align="left">
//         资产管理
//       </Typography>
//       <GreenButton
//         variant="contained"
//         onClick={onRefresh}
//         disabled={refreshing}
//         startIcon={refreshing ? (
//           <CircularProgress size={20} sx={{ color: '#000000' }} />
//         ) : (
//           <RefreshIcon />
//         )}
//       >
//         刷新
//       </GreenButton>
//     </Box>
//   );
// };