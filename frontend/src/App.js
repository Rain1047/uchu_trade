import React from 'react';
import '@fontsource/inter';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './account/dashboard'; // 导入Dashboard组件
import Positions from "./account/positions"; // 导入App样式
import './App.css';
import TradeHistoryTable from "./trade/history";
import { darkTheme} from "./theme";
import './index.css';
import { createTheme, ThemeProvider } from '@material-ui/core/styles';
import './styles/global.css';
import Layout from './components/Layout';
import {Container, Typography} from "@material-ui/core";
import StrategyPage from "./features/strategy"
import BalanceList from "./features/balance"

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('App error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <Container>
                    <Typography variant="h6" color="error">
                        Application error. Please refresh the page.
                    </Typography>
                </Container>
            );
        }

        return this.props.children;
    }
}


function App() {
  return (
      <ErrorBoundary>
            <ThemeProvider theme={darkTheme}>
                <Router>
                    <Layout>
                        <Routes>
                            <Route path="/account/dashboard" element={<Dashboard />} />
                            <Route path="/account/positions" element={<Positions />} />
                            <Route path="/trade/order" element={<Positions />} />
                            <Route path="/trade/history" element={<TradeHistoryTable />} />
                            <Route path="/strategy" element={<StrategyPage />} />
                            <Route path="/balance" element={<BalanceList />} />
                        </Routes>
                    </Layout>
                </Router>
            </ThemeProvider>
        </ErrorBoundary>
  );
}

export default App;
