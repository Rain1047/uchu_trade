import React from 'react';
import '@fontsource/inter';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import TradeHistoryTable from "./features/trade/components/history";
import { darkTheme} from "./theme";
import './index.css';
import { createTheme, ThemeProvider } from '@material-ui/core/styles';
import './styles/global.css';
import Layout from './components/Layout';
import {Container, Typography} from "@material-ui/core";
import StrategyPage from "./features/strategy"
import BalanceList from "./features/balance"
import Backtest from "./features/backtest";
import StrategyFilesPage from "./features/strategyfiles";
import {TradeRecordTable} from "./features/record"

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
                            <Route path="/trade/history" element={<TradeHistoryTable />} />
                            <Route path="/strategy" element={<StrategyPage />} />
                            <Route path="/balance" element={<BalanceList />} />
                            <Route path="/backtest" element={<Backtest />} />
                            <Route path="/strategyfiles" element={<StrategyFilesPage />} />
                            <Route path="/record" element={<TradeRecordTable />} />
                        </Routes>
                    </Layout>
                </Router>
            </ThemeProvider>
        </ErrorBoundary>
  );
}

export default App;
