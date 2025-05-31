
列表

支持分页面查询 - POST
http://localhost:8000/api/record/list_spot_record
```python
class TradeRecordPageRequest(BaseModel):
    pageSize: int = 10
    pageNum: int = 1
    # 交易符号
    ccy: str = ''
    # 交易类别
    type: str = ''
    # 交易方向
    side: str = ''
    # 交易状态
    status: str = ''
    # 交易方式
    exec_source: str = ''
    begin_time: str = ''
    end_time: str = ''
```


| 展示列       | 对应符号        | 是否为搜索条件 | 搜索条件类型 | 搜索方式                  |
|-----------|-------------|---------|--------|-----------------------|
| 符号        | ccy         | 是       | 输入框    | 模糊搜索                  |
| 交易类别      | type        | 是       | 枚举下拉多选 | 精准匹配-多选               |
| 交易方向      | side        | 是       | 枚举下拉单选 | 精准匹配-单选               |
| 数量，单位USDT | amount      | 否       |        |                       |
| 交易价格      | exec_price  | 否       |        |                       |
| 交易方式      | exec_source | 是       | 枚举下拉单选 | 精准匹配-单选               |
| 交易时间      | uTime       | 是       | 时间组件   | 时间范围筛选，支持近一个月，近三月，近一年 |
| 交易日志      | note        | 否       |        |                       |

