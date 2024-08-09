import React from 'react';
import '@fontsource/inter';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './account/dashboard'; // 导入Dashboard组件
import Positions from "./account/positions"; // 导入App样式
import './App.css';
import DataGridDemo from "./account/tradetable.";
import CollapsibleDataGrid from "./account/CollapsDataGrid";

function App() {
  return (
      <Router>
        <Routes> {/* Updated from Switch to Routes */}
          <Route path="/account/dashboard" element={<Dashboard />} />
          <Route path="/account/positions" element={<Positions />} />
            <Route path="/trade/order" element={<Positions />} />
            <Route path="/account/tradetable" element={<DataGridDemo />} />
            <Route path="/account/collapsgrid" element={<CollapsibleDataGrid />} />
        </Routes>
      </Router>
  );
}

export default App;
