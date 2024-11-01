class StdResult:
    @staticmethod
    def success(data=None, message="Operation successful"):
        return {
            "success": True,
            "message": message,
            "data": data
        }

    @staticmethod
    def error(message="Operation failed", data=None):
        return {
            "success": False,
            "message": message,
            "data": data
        }


class StdPageResult(StdResult):
    @staticmethod
    def success(items, page_size, page_num, total_count, message="Data retrieved successfully"):
        return {
            "success": True,
            "message": message,
            "data": {
                "items": items,
                "total_count": total_count,
                "page_size": page_size,
                "page_num": page_num
            }
        }


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
