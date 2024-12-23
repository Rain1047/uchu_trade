基于api返回的DICT结果，提供SQLITE的建表语句，和基于于
from sqlalchemy.ext.declarative import declarative_base的python对象，使用下划线代替驼峰

基于这个object类生成sqlite的建表sql，携带上注释的内容

#p 用于全局搜索，快速定位

# DAO层通用方法实现 PROMPT

请基于给定的类，实现以下标准DAO方法：

1. 基础转换方法:
   - to_dict(): 将对象转换为字典
     - 返回: Dict[str, Any]
     - 注意处理日期时间等特殊类型的序列化

2. 单记录操作:
   - insert(data: Dict[str, Any]) -> bool
     - 异常处理：捕获并记录数据库异常
     - 事务处理：确保原子性
   
   - get_by_id(id: int) -> Optional[Dict[str, Any]]
     - 返回None如果记录不存在
     - 使用to_dict()进行转换
   
   - delete_by_id(id: int) -> bool
     - 支持软删除（is_del字段）
     - 事务处理和异常捕获
   
   - update_selective_by_id(id: int, data: Dict[str, Any]) -> bool
     - 只更新非空字段
     - 事务和异常处理

3. 批量查询操作:
   - list_by_{condition}(**kwargs) -> [str, List[Dict[str, Any]]
     - 支持分页参数（page_num, page_size）
     - 支持排序参数（sort_field, sort_order）
     - 返回格式：[item.to_dict() for item in items]
     - 空结果返回：[]

4. 批量更新操作:
   - batch_create_or_update(items: List[Dict[str, Any]]) -> bool
     实现批量Upsert（更新+插入）功能：
     - 输入校验：检查必填字段
     - 更新逻辑：
       * 有ID -> 更新现有记录
       * 无ID -> 创建新记录
       * 未包含 -> 软删除(is_del=1)
     - 事务管理：
       * 原子性保证
       * 异常回滚
     - 性能优化：
       * 批量操作
       * 减少数据库查询

注意事项：
1. 所有方法都需要添加适当的日志记录
2. 使用类型注解提高代码可读性
3. 添加必要的参数验证
4. 统一的异常处理机制
5. 考虑并发场景下的数据一致性

