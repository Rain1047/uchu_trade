import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Switch, Box, Typography } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
    switchWrapper: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: theme.spacing(0.5, 2),
        minWidth: 120,
        '& .MuiSwitch-root': {
            marginLeft: theme.spacing(1)
        }
    }
}));

const TradeSwitch = ({ checked, onChange, label }) => {
    const classes = useStyles();

    return (
        <Box className={classes.switchWrapper}>
            <Typography variant="body2">{label}</Typography>
            <Switch
                checked={checked}
                onChange={onChange}
                color="primary"
                size="small"
            />
        </Box>
    );
};

export default TradeSwitch;