import React from 'react';
import Balance from '././balance'; // 导入Balance组件
import Order from '../trade/order'; // 导入Order组件
import './dashboard.css'; // 导入Dashboard样式

function Dashboard() {
    return (
        <div className="dashboard">
            <div className="dashboard-balance">
                <Balance />
            </div>
            <div className="dashboard-order">
                <Order />
            </div>
        </div>
    );
}

export default Dashboard;