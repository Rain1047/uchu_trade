# 页面
http://localhost:3000/
frontend/src/App.js

http://localhost:3000/enhanced-backtest 回测功能（新）
frontend/src/components/BacktestInterface.js
frontend/src/pages/BacktestDetail.js
frontend/src/pages/BacktestInterface.js


http://localhost:3000/backtest 回测功能（旧）
    - http://127.0.0.1:8000/api/backtest/run_backtest 运行回测
    
    controller: backend/controller_center/backtest/backtest_controller.py 
        @router.post("/run_backtest") 
    service: /backtest_center/backtest_main.py 的 backtest_main


http://localhost:3000/strategy-instance 实例管理
front: frontend/src/pages/StrategyInstance.js
controller: backend/controller/strategy_instance_controller.py


http://localhost:3000/agent/chat agent对话入口


http://localhost:3000/record 交易记录


# 样式
绿色：#5eddac


# 数据库
db_absolute_path = project_root / 'backend' / 'trade_db.db'
数据库链接和CRUD 参考 backend/_utils.py DatabaseUtils
