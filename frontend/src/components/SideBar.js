import React from 'react';
import { Link } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import {
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    IconButton,
    Divider
} from '@material-ui/core';
import {
    Dashboard as DashboardIcon,
    ShowChart as ShowChartIcon,
    History as HistoryIcon,
    SwapHoriz as SwapHorizIcon,
    ChevronLeft as ChevronLeftIcon,
    Menu as MenuIcon,
    Settings as SettingsIcon,
    AccountBalance as AccountBalanceIcon,
    Assessment as AssessmentIcon,
    Receipt as ReceiptIcon,
} from '@material-ui/icons';

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
    drawer: {
        width: drawerWidth,
        flexShrink: 0,
        whiteSpace: 'nowrap',
    },
    drawerOpen: {
        width: drawerWidth,
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    },
    drawerClose: {
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
        overflowX: 'hidden',
        width: theme.spacing(7) + 1,
    },
    toolbar: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: theme.spacing(0, 1),
        height: '64px',
    },
    listItem: {
        '&.active': {
            backgroundColor: theme.palette.action.selected
        }
    }
}));

const SideBar = ({ open, setOpen }) => {
    const classes = useStyles();

    const menuItems = [
        {
            text: 'Agent',
            icon: <SettingsIcon />,
            path: '/'
        },
        {
            text: 'Record',
            icon: <HistoryIcon />,
            path: '/record'
        },
        {
            text: 'Balance',
            icon: <AccountBalanceIcon />,
            path: '/balance'
        },
        {
            text: 'Strategy',
            icon: <SettingsIcon />,
            path: '/strategy'
        },
        {
            text: 'Backtest',
            icon: <AssessmentIcon />,
            path: '/backtest'
        }
    ];

    return (
        <Drawer
            variant="permanent"
            className={`${classes.drawer} ${open ? classes.drawerOpen : classes.drawerClose}`}
            classes={{
                paper: `${open ? classes.drawerOpen : classes.drawerClose}`,
            }}
        >
            <div className={classes.toolbar}>
                <IconButton onClick={() => setOpen(!open)}>
                    {open ? <ChevronLeftIcon /> : <MenuIcon />}
                </IconButton>
            </div>
            <Divider />
            <List>
                {menuItems.map((item) => (
                    <ListItem
                        button
                        key={item.text}
                        component={Link}
                        to={item.path}
                        className={classes.listItem}
                    >
                        <ListItemIcon style={{ color: 'inherit' }}>
                            {item.icon}
                        </ListItemIcon>
                        <ListItemText primary={item.text} style={{
                            opacity: open ? 1 : 0,
                            display: open ? 'block' : 'none'
                        }} />
                    </ListItem>
                ))}
            </List>
        </Drawer>
    );
};

export default SideBar;