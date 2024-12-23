基于api返回的DICT结果，提供SQLITE的建表语句，和基于于
from sqlalchemy.ext.declarative import declarative_base的python对象，使用下划线代替驼峰

基于这个object类生成sqlite的建表sql，携带上注释的内容

#p 用于全局搜索，快速定位

#p DAO PROMPT
在这个类的基础上，添加
    to_dict()方法，返回dict
    insert()方法：入参为dict，返回布尔类型
    get_by_id()方法，返回dict类型
    list_by_{condition} 方法，返回dict(list)类型，条件为{condition}
        注意这里是dict[list]:
        return {'strategy_list': [result.to_dict() for result in results]} if results else {'strategy_list': []}
    delete_by_id()方法，返回布尔
    update_selective_by_id() 方法，返回布尔
    batch_crate_or_update() 方法，参数为list[dict]，返回布尔
        (Bulk Upsert)功能，具体需求如下：
        1. 输入：包含多条记录的列表，每条记录可能是新增或更新
        2. 判断逻辑：
          - 如果记录带有ID，则更新已存在记录
          - 如果记录没有ID，则新增记录
          - 对于已存在但输入列表中未包含的记录，需要软删除(将is_del设为1)
        3. 其他要求：
          - 需要支持事务
          - 需要进行异常处理
          - 所有操作应该是原子的(要么全部成功，要么全部失败)

请帮我实现这个功能，使用[期望的编程语言]。

在这个页面上增加“运行回测”的按钮，按钮的位置在策略的输入框之后，回测记录之前。回测需要加一个loading判断是否执行完成。完成后自动取

在对象中实现：
1. list查询和get_by_id方法
2. 根据api结果插入表，如果xxx字段已存在，则改为更新
3. 根据id删除表中的数据

可选功能：
1. 根据

