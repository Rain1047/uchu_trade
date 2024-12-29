[balance-prompt] design

页面整体布局：一个加密货币资产管理页面，包含：
- 顶部标题"资产管理"和刷新按钮
- 主体为资产列表表格

表格结构：表格需要包含以下列：
- 币种（显示加密货币代号）"ccy"
- 可用余额（数字，保留4位小数）"avail_eq"
- 账户权益($)（数字，保留4位小数）"eq_usd"
- 持仓均价($)（数字，保留4位小数）"acc_avg_px"
- 总收益率（百分比，正值显示绿色，负值显示红色）"spot_upl_ratio"
- 限价（开关按钮）limit_order_switch为"true"时显示开，为"false"时显示关
- 止损（开关按钮）stop_loss_switch为"true"时显示开，为"false"时显示关
- 操作（查看&编辑按钮）

表格对应请求 GET http://localhost:8000/api/balance/list_balance
具体请求和返回结果：见 [balance-prompt] api 

交互要求：
- 刷新按钮点击时重新加载数据 
- 限价和止损为可切换的开关按钮
  - 点击按钮之后，请求POST http://127.0.0.1:8000/api/balance/update_account_balance_config_switch
  - 具体请求和返回结果：见 [balance-prompt] api 
  
- "查看&编辑"按钮使用镂空样式，hover时有背景色变化
  - 点击按钮后，需要侧拉弹出一个侧边栏，侧边栏内容包含：
    - 顶部标题"配置详情" 和关闭按钮
    - 标题下方为 切换按钮 "限价" 和 "止损" 限价对应"limit_order"状态，止损对应"stop_loss"状态
    - 资产配置列表，内容来源为请求GET http://localhost:8000/api/balance/list_configs/ETH/{type}?type_=stop_loss
    - 列表每行包含以下列：
      - 符号（EMA、SMA、USDT）"indicator"
      - 符号值（数字，整数）"indicator_val"
      - 目标价格（数字，整数）"target_price"
      - 百分比值（百分比，整数）"percentage"
      - 数量（数字，整数）"amount"
      - 开关按钮（开&关）"switch" 为0时显示开，为1时显示关
      - 操作（删除按钮）
    - 列的最下面有新增按钮，点击之后，可以新增一行配置
    - 最下方有保存按钮，点击之后，请求POST http://127.0.0.1:8000/api/balance/save_config
      - save_config时，实现批量Upsert（更新+插入）功能：
      - 输入校验：检查必填字段
      - 更新逻辑：
        * 有ID -> 更新现有记录
        * 无ID -> 创建新记录
        * 未包含 -> 软删除(is_del=1)

样式要求
- 基于material深色主题进行设计
- 保持代码整体的风格

