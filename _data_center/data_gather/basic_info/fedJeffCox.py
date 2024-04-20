from datetime import datetime
from datetime import date
import requests
from bs4 import BeautifulSoup


def get_jeff_cox_list():
    """
    获取jeff_cox的新闻列表，通过调度器调用
    """
    url = "https://www.cnbc.com/jeff-cox/"
    div = "RiverCard-standardBreakerCard RiverCard-specialReportsRiver RiverCard-card"

    # 发送HTTP请求并获取页面内容
    response = requests.get(url)
    fed_list = []
    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找指定class为"RenderKeyPoints-list"的div元素
        key_points_divs = soup.find_all('div', class_=div)

        # 获取div元素的内容
        for div in key_points_divs:
            link = div.find('a', class_='RiverCard-mediaContainer')['href']
            fed_list.append(link)
        return fed_list
    else:
        print("无法获取页面内容，状态码：", response.status_code)


def store_jeff_cox_detail():
    pass

if __name__ == "__main__":
    print(get_jeff_cox_list())


