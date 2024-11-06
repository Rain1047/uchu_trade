import React, {useCallback, useState} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {Box, Container, Typography} from '@material-ui/core';
import SideBar from './SideBar';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Layout error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <Container>
                    <Typography variant="h6" color="error">
                        Something went wrong. Please refresh the page.
                    </Typography>
                </Container>
            );
        }

        return this.props.children;
    }
}

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
    },
    contentWrapper: {
        flexGrow: 1,
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center', // 水平居中
    },
    content: {
        width: '100%',
        maxWidth: '1200px', // 可以根据需要调整最大宽度
        padding: theme.spacing(3),
        marginTop: '64px', // 为顶部工具栏留出空间
    }
}));

const Layout = ({ children }) => {
    const classes = useStyles();
    const [open, setOpen] = useState(true);

    const handleToggle = useCallback(() => {
        setOpen(prev => !prev);
    }, []);

    return (
        <ErrorBoundary>
            <Box className={classes.root}>
                <SideBar open={open} setOpen={handleToggle} />
                <Box className={classes.contentWrapper}>
                    <Container className={classes.content}>
                        {children}
                    </Container>
                </Box>
            </Box>
        </ErrorBoundary>
    );
};

export default Layout;