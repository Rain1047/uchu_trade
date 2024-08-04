import requests
from bs4 import BeautifulSoup

# 定义网页URL
url1= "https://www.cnbc.com/2021/11/02/federal-reserve-investors-seek-clues-on-interest-rate-hikes.html"

url2 = "https://www.cnbc.com/2021/11/03/fed-decision-taper-timetable-as-it-starts-pulling-back-on-pandemic-era" \
       "-economic-aid-.html"

# 发送HTTP请求并获取页面内容
response = requests.get(url2)

# 检查请求是否成功
if response.status_code == 200:
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找指定class为"RenderKeyPoints-list"的div元素
    key_points_div = soup.find('div', class_='RenderKeyPoints-list')

    info_div = soup.find('div', class_='ArticleBody-articleBody')

    # 打印div元素的内容
    if key_points_div:
        res = key_points_div.get_text()
        print("Key Points结果为：{}".format(res))
    else:
        print("未找到指定的div元素。")

    if info_div:
        info = info_div.get_text()
        print("文章结果为：{}".format(info))
else:
    print("无法获取页面内容，状态码：", response.status_code)


