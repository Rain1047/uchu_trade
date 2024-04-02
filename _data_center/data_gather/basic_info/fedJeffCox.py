from datetime import datetime
from datetime import date
import requests
from bs4 import BeautifulSoup


def get_jeff_cox_list():
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
        else:
            print("未找到指定的div元素。")
        return fed_list
    else:
        print("无法获取页面内容，状态码：", response.status_code)


def get_daily_news(fed_list):
    todayDate = date.today()
    # 提取年月日部分
    year = todayDate.year
    month = todayDate.month
    day = todayDate.day

    # 创建新的只含有年月日的date对象
    todayDate = date(year, month, day)

    tryDate = date(2023, 12, 1)

    print("今日时间: {}".format(todayDate))

    for item in fed_list:
        year = int(item.split("/")[3])
        month = int(item.split("/")[4])
        day = int(item.split("/")[5])
        dateObj = date(year, month, day)
        if tryDate == dateObj:
            print("Today the fed news {}: {}".format(tryDate, item))
            # 需要处理item，调用openAI API接口


if __name__ == "__main__":
    print(get_jeff_cox_list())