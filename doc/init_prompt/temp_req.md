我想将回测部分的功能进行一系列的强化，下面是我的计划：
1. http://localhost:3000/enhanced-backtest 回测功能（新）从页面的整体结构上，参考http://localhost:3000/strategy-instance 实例管理。具体如下：
0.1 布局为右上方同位置为：“创建回测”按钮和“刷新”（样式保持一致），已完成
而点击“创建回测”之后，弹出的框为回测配置的表单。
点击”开始回测“后，创建一条回测记录，展示到下方的位置。
    注意⚠️ 这里需要参考- http://127.0.0.1:8000/api/backtest/run_backtest 运行回测方法。
    将配置的入参数通过该链路回测，如果有默认值的话需要初始化
0.3 下方的列表，会展示回测记录id，策略组合，频率，状态（运行中、分析中、已结束）、回测时间段，获利次数/总交易次数/胜率，策略运行时间，列表的结尾增加详情按钮，无其它按钮
    注意⚠️ 1. 这里策略组合列的宽度可以适当调整窄一些。 2. 获利次数/总交易次数/胜率调整为获利测树/亏损次数/胜率 3. 加一列 盈利平均收益/亏损平均收益/盈亏比 4. 去掉运行时间，没有什么意思

0.4 点击详情后仍然是一个总结+列表的形式。（由于我们回测的时候会选择多个交易对，所以这里是一个列表）；总结即为 回测交易对数 ，盈利个数，亏损个数，总胜率。
    注意⚠️ 这里我还没有测试到
下方的列表展示：交易对、交易次数、盈利次数、亏损次数、胜率、平均单笔盈利金额、平均单笔亏损金额、盈亏比、总盈利 （这里我希望可以根据胜率、盈亏比、总盈利做一个排序按钮），列表为分页查询
    注意⚠️ 这里我还没有测试到

针对而点击“创建回测”之后，弹出的框为回测配置的表单。
点击”开始回测“后，创建一条回测记录，展示到下方的位置。我需要以下修改：
    注意⚠️ 这里需要参考- http://127.0.0.1:8000/api/backtest/run_backtest 运行回测方法
    1. 这里首先你需要查看完整的链路http://127.0.0.1:8000/api/backtest/run_backtest和调用的方法backend/controller_center/backtest/backtest_service.py 你需要整理出这个过程回测干了什么，插入了哪些数据。这些都需要理清楚。
    2. 当我在http://localhost:3000/enhanced-backtest 页面点击创建回测，并且点击开始后，调用了：
    http://localhost:8000/api/enhanced-backtest/run
        {
            "entry_strategy": "dbb_entry_long_strategy",
            "entry_strategy": "dbb_exit_long_strategy",
            "filter_strategy": "sma_perfect_order_filter_strategy",
            "symbols": [
                "DOGE",
                "BTC",
                "ETH"
            ],
            "timeframe": "4h",
            "backtest_period": "1m",
            "initial_cash": 100000,
            "risk_percent": 2,
            "commission": 0.001,
            "save_to_db": true,
            "description": "前端创建的回测"
        }
    我希望的逻辑和结果是：
        1. 你将symbols里面的每一个symbol都进行回测，回测按照entry_strategy、entry_strategy、filter_strategy进行入场离场止损等。backtest_period代表你回测的时间段。     
        2. 我希望的结果是DOGE、BTC、ETH分别回测了从2025年5月1日-2025年5月31（假设今天是5月31日）依据上述策略在4小时窗口上的表现。
    以及我希望在http://localhost:3000/enhanced-backtest中，缩短策略组合的列宽，在操作中添加删除，并提供后端的接口。

    将配置的入参数通过该链路回测，如果有默认值的话需要初始化
0.3 下方的列表，会展示回测记录id，策略组合，频率，状态（运行中、分析中、已结束）、回测时间段，获利次数/总交易次数/胜率，策略运行时间，列表的结尾增加详情按钮，无其它按钮
    注意⚠️ 1. 这里策略组合列的宽度可以适当调整窄一些。 




0.4 点击详情后仍然是一个总结+列表的形式。（由于我们回测的时候会选择多个交易对，所以这里是一个列表）；总结即为 回测交易对数 ，盈利个数，亏损个数，总胜率。
    注意⚠️ 这里我还没有测试到
下方的列表展示：交易对、交易次数、盈利次数、亏损次数、胜率、平均单笔盈利金额、平均单笔亏损金额、盈亏比、总盈利 （这里我希望可以根据胜率、盈亏比、总盈利做一个排序按钮），列表为分页查询
    注意⚠️ 这里我还没有测试到



针对而点击“创建回测”之后，弹出的框为回测配置的表单。
点击”开始回测“后，创建一条回测记录，展示到下方的位置。我需要以下修改：
    注意⚠️ 这里需要参考- http://127.0.0.1:8000/api/backtest/run_backtest 运行回测方法
    1. 这里首先你需要查看完整的链路http://127.0.0.1:8000/api/backtest/run_backtest和调用的方法backend/controller_center/backtest/backtest_service.py 你需要整理出这个过程回测干了什么，插入了哪些数据。这些都需要整理清楚
    2. 在http://localhost:3000/backtest 页面中
    http://127.0.0.1:8000/api/backtest/get_backtest_detail?key=ETH-USDT_ST2_202505311158 方法（实例）展示了ETH在双布林带的回测情况
    我希望在点http://localhost:3000/enhanced-backtest击详情后仍然是一个总结+列表的形式。（由于我们回测的时候会选择多个交易对，所以这里是一个列表）；总结即为 回测交易对数 ，盈利个数，亏损个数，总胜率。

    2. 当我在http://localhost:3000/enhanced-backtest 页面点击创建回测，并且点击开始后，调用了：
    http://localhost:8000/api/enhanced-backtest/run
        {
            "entry_strategy": "dbb_entry_long_strategy",
            "entry_strategy": "dbb_exit_long_strategy",
            "filter_strategy": "sma_perfect_order_filter_strategy",
            "symbols": [
                "DOGE",
                "BTC",
                "ETH"
            ],
            "timeframe": "4h",
            "backtest_period": "1m",
            "initial_cash": 100000,
            "risk_percent": 2,
            "commission": 0.001,
            "save_to_db": true,
            "description": "前端创建的回测"
        }
    我希望的逻辑和结果是：
        1. 你将symbols里面的每一个symbol都进行回测，回测按照entry_strategy、entry_strategy、filter_strategy进行入场离场止损等。backtest_period代表你回测的时间段。  
        2. 我希望的结果是DOGE、BTC、ETH分别回测了从2025年5月1日-2025年5月31（假设今天是5月31日）依据上述策略在4小时窗口上的表现。
    以及我希望在http://localhost:3000/enhanced-backtest中
        3. 一定要！！！一定要记录数据！！！一定要记录数据！！！用于后续的详情接口。
    
    页面上：缩短策略组合的列宽！！！
        列表页：增加一列，交易对 - 展示回测的所有交易对
        点击详情后，仍然为一个列表页，展示了交易对纬度的回测结果。

   
   
    将配置的入参数通过该链路回测，如果有默认值的话需要初始化
0.3 下方的列表，会展示回测记录id，策略组合，频率，状态（运行中、分析中、已结束）、回测时间段，获利次数/总交易次数/胜率，策略运行时间，列表的结尾增加详情按钮，无其它按钮
    注意⚠️ 1. 这里策略组合列的宽度可以适当调整窄一些。 


尽管还有一些问题，但是数据已经可以跑通了，但是我们紧接着要做更多的优化：
1. 页面的`策略组合` 列还是太宽了，列宽缩短列宽缩短
2. 在http://localhost:3000/enhanced-backtest/6 页，列表的左上方 和排序等按钮同位置的地方加一个按钮和一个下拉框
    按钮为“总览”，显示的内容和当前一致。 下拉框的内容是根据交易对动态展示的 这里下拉的选项就有BTC和ETH；
    点击下拉后，展示的内容参考http://127.0.0.1:8000/api/backtest/get_backtest_detail?key=ETH-USDT_ST2_202505311158 接口；
    方法对应 backend/controller_center/backtest/backtest_service.py 的get_backtest_detail方法，但是这里的数据需要根据新的
    方法进行调整（创建新的表enhenced_backtest_record_detail）参考 backend/data_object_center/backtest_record.py 对象
    但是注意是参考不是copy，需要考虑我的需求设计新的数据接口


几个问题：
1. 运行 http://localhost:8000/api/enhanced-backtest/run 后，页面一直在loading，这个应该是异步的，而且策略的状态应该是运行中。（添加运行失败的状态）
2. 总览和选择交易对的按钮位置和样式不对，位置是表格的左上方和排序按钮在同一个水平线；下拉框除了交易对外，添加默认初始值为“全部”
3. EnhancedBacktestRecordDetail的数据结构不对，我希望是每一次交易的记录。像这样：
```json
"records": [
            {
                "id": 4900,
                "back_test_result_key": "BTC-USDT_ST8_202505262300",
                "transaction_time": "2024-01-08",
                "transaction_result": "Price: 43889.49, Size: -0.04520308275983806, PnL: -18.0436914916723",
                "transaction_pnl": -18.04
            },
            {
                "id": 4901,
                "back_test_result_key": "BTC-USDT_ST8_202505262300",
                "transaction_time": "2024-01-09",
                "transaction_result": "Price: 45802.74690067212, Size: -0.04479791142013803, PnL: 50.215956907575",
                "transaction_pnl": 50.22
            },
            {
                "id": 4902,
                "back_test_result_key": "BTC-USDT_ST8_202505262300",
                "transaction_time": "2024-01-12",
                "transaction_result": "Price: 46313.99, Size: -0.042510910610217494, PnL: -33.68198920411476",
                "transaction_pnl": -33.68
            },
            {
                "id": 4903,
                "back_test_result_key": "BTC-USDT_ST8_202505262300",
                "transaction_time": "2024-01-17",
                "transaction_result": "Price: 42772.57, Size: -0.04623644742098439, PnL: -24.165598072247246",
                "transaction_pnl": -24.17
            },
            {
                "id": 4904,
                "back_test_result_key": "BTC-USDT_ST8_202505262300",
                "transaction_time": "2024-01-29",
                "transaction_result": "Price: 42191.31579222075, Size: -0.04842212972003886, PnL: 41.62387946554832",
                "transaction_pnl": 41.62
            },
            {
                "id": 4905,
                "back_test_result_key": "BTC-USDT_ST8_202505262300",
                "transaction_time": "2024-01-31",
                "transaction_result": "Price: 43106.96402353743, Size: -0.04690518059361024, PnL: 19.799007856337",
                "transaction_pnl": 19.8
            },
```
当然可以在接口里面添加一个总览，如：
```json
"results": {
            "symbol": "BTC-USDT",
            "strategy_name": "BTC双布林带策略",
            "test_finished_time": "2025-05-26 23:00:09",
            "buy_signal_count": 119,
            "sell_signal_count": 80,
            "transaction_count": 89,
            "profit_count": 32,
            "loss_count": 56,
            "profit_total_count": 1111.0,
            "profit_average": 29.0,
            "profit_rate": 35.0,
            "strategy_id": "8",
            "gmt_create": "2025-05-26 23:00:09",
            "gmt_modified": "2025-05-26 23:00:09"
        },
```
但是我的数据结构是参考，注意也只是参考。具体实现你可以重新设计
    {
        "id": 4905,
        "back_test_result_key": "BTC-USDT_ST8_202505262300",
        "transaction_time": "2024-01-31",
        "transaction_result": "Price: 43106.96402353743, Size: -0.04690518059361024, PnL: 19.799007856337",
        "transaction_pnl": 19.8
    },
然后下拉选择一个交易对后获得上面的内容，展示的话添加图表，参考http://localhost:3000/backtest