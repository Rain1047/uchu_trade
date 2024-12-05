import React from 'react';
import { Box, Typography, Button, CircularProgress } from '@material-ui/core';
import { Refresh as RefreshIcon } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';

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