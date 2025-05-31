我想将回测部分的功能进行一系列的强化，下面是我的计划：
1. http://localhost:3000/enhanced-backtest 回测功能（新）从页面的整体结构上，参考http://localhost:3000/strategy-instance 实例管理。具体如下：
0.1 布局为右上方同位置为：“创建回测”按钮和“刷新”（样式保持一致），已完成
而点击“创建回测”之后，弹出的框为回测配置的表单。
点击”开始回测“后，创建一条回测记录，展示到下方的位置。
    注意⚠️ 这里需要参考- http://127.0.0.1:8000/api/backtest/run_backtest 运行回测方法。
    将配置的入参数通过该链路回测，如果有默认值的话需要初始化
0.2 表单上增加“回测时间段”下拉选项（最近一月、最近3月、最近1年）已完成
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
