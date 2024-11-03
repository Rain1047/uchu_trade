class StdResult:
    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data

    def is_success(self) -> bool:
        """判断操作是否成功"""
        return self.success

    def get_message(self) -> str:
        """获取消息"""
        return self.message

    def get_data(self):
        """获取数据"""
        return self.data

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }

    @classmethod
    def success(cls, data=None, message="Operation successful"):
        """创建成功结果"""
        return cls(True, message, data)

    @classmethod
    def error(cls, message="Operation failed", data=None):
        """创建失败结果"""
        return cls(False, message, data)


class StdPageResult(StdResult):
    def __init__(self, success: bool, message: str, items=None, page_size=10, page_num=1, total_count=0):
        super().__init__(success, message, {
            "items": items or [],
            "total_count": total_count,
            "page_size": page_size,
            "page_num": page_num
        })
        self.items = items or []
        self.page_size = page_size
        self.page_num = page_num
        self.total_count = total_count

    def get_items(self):
        """获取分页项目"""
        return self.items

    def get_total_count(self) -> int:
        """获取总数"""
        return self.total_count

    def get_page_size(self) -> int:
        """获取每页大小"""
        return self.page_size

    def get_page_num(self) -> int:
        """获取页码"""
        return self.page_num

    @classmethod
    def success(cls, data=None, message="Operation successful"):
        """
        Override success method to handle pagination specific data
        """
        if isinstance(data, dict) and all(k in data for k in ["items", "page_size", "page_num", "total_count"]):
            return cls(True, message, data)

        # 构造分页数据结构
        page_data = {
            "items": data.get("items", []),
            "total_count": data.get("total_count", 0),
            "page_size": data.get("page_size", 10),
            "page_num": data.get("page_num", 1)
        }
        return cls(True, message, page_data)

    @classmethod
    def error(cls, message="Operation failed", data=None):
        """创建失败的分页结果"""
        return cls(False, message)



if __name__ == '__main__':
    # Example usage:
    result1 = StdResult.success("This is a success message")
    result2 = StdResult.error("This is an error message")

    # For paginated result
    paginated_result = StdPageResult.success(
        items=["item1", "item2"],
        page_size=10,
        page_num=1,
        total_count=100
    )

    print(result1)
    print(result2)
    print(paginated_result)
