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

表格对应请求：
```
curl -X 'GET' \
  'http://localhost:8000/api/balance/list_balance' \
  -H 'accept: application/json'
```
返回结果：见 [balance-prompt] api 

交互要求：
- 刷新按钮点击时重新加载数据 
- 限价和止损为可切换的开关按钮
  - 点击按钮之后，需要请求
- "查看&编辑"按钮使用镂空样式，hover时有背景色变化

样式要求
- 基于material深色主题进行设计
- 保持代码整体的风格

