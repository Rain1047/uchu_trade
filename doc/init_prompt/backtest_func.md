第一次交互：
http://localhost:3000/backtest 回测功能页面（旧）
    - http://127.0.0.1:8000/api/backtest/run_backtest 运行回测功能（旧）
    
    controller: backend/controller_center/backtest/backtest_controller.py 
        @router.post("/run_backtest") 
    service: /backtest_center/backtest_main.py 的 backtest_main
        backend/backtest_center/backtest_core/backtest_system.py run方法
        `def run(self, df: pd.DataFrame, st: StrategyInstance, plot: bool = False) -> dict:` 


http://localhost:3000/enhanced-backtest 回测功能页面（新）
frontend/src/components/BacktestInterface.js
frontend/src/pages/BacktestDetail.js
frontend/src/pages/BacktestInterface.js


    - http://localhost:8000/api/enhanced-backtest/run 运行回测功能（新）
    ```json 
    POST Request
    {
        "entry_strategy": "dbb_entry_long_strategy",
        "exit_strategy": "dbb_exit_long_strategy",
        "filter_strategy": "sma_perfect_order_filter_strategy",
        "symbols": [
            "BTC",
            "ETH"
        ],
        "timeframe": "4h",
        "backtest_period": "3m",
        "initial_cash": 100000,
        "risk_percent": 2,
        "commission": 0.001,
        "save_to_db": true,
        "description": "前端创建的回测"
    }
    ```
    service: 

    现在我的问题和需求是：需要把- http://localhost:8000/api/enhanced-backtest/run 运行回测功能（新）的方法，
    基于新的请求，复用老的backend/backtest_center/backtest_core/backtest_system.py run方法，（复用backtrader）
    这个有些复杂，需要你仔细浏览代码和逻辑，给出你计划的步骤，原则是老功能不变，但是新的复用老的框架，根据请求重写（复用backtrader）
    然后回测给出更加详细的说明日志


第二次交互：
