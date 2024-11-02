import React from 'react';
import '@fontsource/inter';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './account/dashboard'; // 导入Dashboard组件
import Positions from "./account/positions"; // 导入App样式
import './App.css';
import DataGridDemo from "./account/tradetable.";
import CollapsibleDataGrid from "./account/CollapsDataGrid";
import TradeHistoryTable from "./trade/history";
import './index.css';
import { createTheme, ThemeProvider } from '@material-ui/core/styles';

const darkTheme = createTheme({
  palette: {
    type: 'dark',
    primary: {
      main: '#5eddac',
    },
    secondary: {
      main: '#f57ad0',
    },
    background: {
      default: '#131313',
      paper: '#222',
    },
    text: {
      primary: '#fff',
      secondary: '#888',
    },
  },
});

function App() {
  return (
      <ThemeProvider theme={darkTheme}>
          <Router>
            <Routes> {/* Updated from Switch to Routes */}
                <Route path="/account/dashboard" element={<Dashboard />} />
                <Route path="/account/positions" element={<Positions />} />
                <Route path="/trade/order" element={<Positions />} />
                <Route path="/account/tradetable" element={<DataGridDemo />} />
                <Route path="/account/collapsgrid" element={<CollapsibleDataGrid />} />
                <Route path="/trade/history" element={<TradeHistoryTable />} />

            </Routes>
          </Router>
    </ThemeProvider>
  );
}

export default App;
