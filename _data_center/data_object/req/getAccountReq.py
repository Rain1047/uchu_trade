# 编写post请求类

# 导入requests模块
import requests


# 定义post请求类
class PostRequest:
    def __init__(self, url, data):
        self.url = url
        self.data = data

    def post(self):
        # 发送post请求
        r = requests.post(self.url, data=self.data)
        return r.text
