import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd

# 导入待测试的路由
from backend.controller_center.backtest.enhanced_backtest_controller import router as backtest_router


def _create_dummy_ohlcv(rows: int = 120):
    """生成满足需求的假K线数据"""
    idx = pd.date_range("2021-01-01", periods=rows, freq="4H")
    data = {
        "open":  [1.0] * rows,
        "high":  [1.5] * rows,
        "low":   [0.5] * rows,
        "close": [1.0] * rows,
        "volume": [100] * rows,
    }
    return pd.DataFrame(data, index=idx)


@pytest.fixture(scope="module")
def test_client():
    """构造包含目标路由的FastAPI测试客户端"""
    app = FastAPI()
    app.include_router(backtest_router)
    return TestClient(app)


def test_run_endpoint_success(test_client):
    """验证 /api/enhanced-backtest/run 在依赖被mock后能返回成功"""
    dummy_df = _create_dummy_ohlcv()

    # Mock 依赖：KlineManager、BacktestRecord、DatabaseUtils、strategy registry
    with patch("backend.controller_center.backtest.enhanced_backtest_controller.EnhancedKlineManager") as MockManager, \
         patch("backend.controller_center.backtest.enhanced_backtest_controller.EnhancedBacktestRecord") as MockRecord, \
         patch("backend.controller_center.backtest.enhanced_backtest_controller.DatabaseUtils") as MockDBUtils, \
         patch("backend.controller_center.backtest.enhanced_backtest_controller.registry") as mock_registry:

        # 配置K线数据返回
        manager_instance = MockManager.return_value
        manager_instance.get_kline_data.return_value = dummy_df

        # 配置回测记录创建返回对象
        record_instance = MagicMock()
        record_instance.id = 42
        MockRecord.create.return_value = record_instance

        # 配置DatabaseUtils session
        db_session = MagicMock()
        db_session.close.return_value = None
        MockDBUtils.get_db_session.return_value = db_session

        # 配置策略仓库
        mock_registry.list_strategies.return_value = [
            {"name": "mock_entry", "type": "entry"},
            {"name": "mock_exit", "type": "exit"},
            {"name": "mock_filter", "type": "filter"},
        ]

        payload = {
            "entry_strategy": "mock_entry",
            "exit_strategy": "mock_exit",
            "filter_strategy": "mock_filter",
            "symbols": ["BTC-USDT"],
            "timeframe": "4h",
            "backtest_period": "2021-01-01/2021-06-01",
            "initial_cash": 10000,
            "risk_percent": 1.0,
            "commission": 0.001,
            "description": "unit-test"
        }

        response = test_client.post("/api/enhanced-backtest/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["record_id"] == 42 