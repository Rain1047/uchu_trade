from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy import exists

from backend.data_center.data_object.dao.fn_instance import FnInstance
from backend.service.utils import DatabaseUtils


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
    global key_points
    jeff_cox_list = get_jeff_cox_list()
    print("Jeff Cox List:", jeff_cox_list)
    session = DatabaseUtils.get_db_session()
    for link in jeff_cox_list:
        response = requests.get(link)
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找指定class为"RenderKeyPoints-list"的div元素
            author_div = soup.find('div', class_="Author-authorNameAndSocial")
            author_name = soup.find('a', class_='Author-authorName').text
            key_points = ""
            print("Author Name:", author_name)
            key_points_div = soup.find('div', class_='RenderKeyPoints-list')
            # judge key_points_div not none
            if key_points_div:
                key_points = key_points_div.get_text()
                print("Key Points结果为：{}".format(key_points))
                # prompt = get_prompt(prompt="key")
                # 在这里调用g4f
                # key_point_analysis = call_g4f(res, prompt)
                # print(key_point_analysis)
            else:
                print("未找到文章的的Key Points。")
            info_div = soup.find('div', class_='ArticleBody-articleBody')
            # judge info_div not none
            if info_div:
                info = info_div.get_text()
                # 打印info的前100字
                print("文章结果为：{}".format(info[:100]))
                # prompt = get_prompt(prompt="content")
                # 在这里调用g4f
                # info_analysis = call_g4f(info, prompt)
                # print(info_analysis)

                # 当info_div不为空时，创建FnInstance对象，插入数据库
                # 检查链接是否已经存在
                if not session.query(exists().where(FnInstance.url == link)).scalar():
                    # 如果链接不存在，则创建FnInstance对象并插入数据库
                    fn_instance = FnInstance()
                    fn_instance.source = "CNBC"
                    fn_instance.author = author_name
                    fn_instance.url = link
                    fn_instance.summary = key_points
                    fn_instance.content = info
                    fn_instance.create_time = datetime.now()
                    session.add(fn_instance)
                    session.commit()
                else:
                    print("链接已存在，不执行插入操作。")
            else:
                print("没有找到该文章的内容")
            print("=============================")
        else:
            print("无法获取页面内容，状态码：", response.status_code)


if __name__ == "__main__":
    print(store_jeff_cox_detail())

