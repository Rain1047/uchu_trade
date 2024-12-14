from datetime import date
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
import g4f


def get_fed_news_links(url, div_class):
    response = requests.get(url)
    fed_news_links = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        key_points_divs = soup.find_all('div', class_=div_class)

        for div in key_points_divs:
            link = div.find('a', class_='RiverCard-mediaContainer')['href']
            print(link)
            fed_news_links.append(link)
    else:
        print("无法获取页面内容，状态码：", response.status_code)

    return fed_news_links


def call_gpt(client, prompt):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # messages=[{"role": "user", "content": "what is the limit size of thw input?"}],
        messages=prompt,
        stream=True, )
    res = ''.join(part.choices[0].delta.content or "" for part in stream)
    return res


def create_prompt(role, content):
    prompt = [{"role": role, "content": content}]
    return prompt


def call_g4f(content, prompt):
    g4f.debug.logging = True  # Enable logging
    g4f.check_version = False  # Disable automatic version checking
    print("start analysis" + g4f.version)  # Check version
    print(g4f.Provider.Ails.params)  # Supported args

    # Automatic selection of provider
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_35_turbo,
        messages=[{"role": "user", "content": "analysis the content:{}".format(content), "prompt": ""}],
    )

    return response


def get_prompt(prompt):
    if prompt == "key":
        prompt1 = "分析这段内容，并总结出要点。"
        prompt2 = "总结出美联储对于加息的态度。"
        prompt3 = "使用中文回复。"
        prompt = prompt1 + prompt2 + prompt3
        return prompt
    if prompt == "content":
        prompt1 = "analysis this content and summarize the key point."
        prompt2 = "tell me the attitude of the fed to increase the rate."
        prompt3 = "translate your answer in chinese."
        prompt = prompt1 + prompt2 + prompt3
        return prompt


def process_fed_news(links, target_date):
    global key_point_analysis
    for link in links:
        year = int(link.split("/")[3])
        month = int(link.split("/")[4])
        day = int(link.split("/")[5])
        date_obj = date(year, month, day)

        if target_date == date_obj:
            print("今日联邦新闻： {}".format(link))
            # 需要处理item，调用OpenAI API接口
            # 此处可以添加处理item的代码，调用OpenAI API等
            response = requests.get(link)
            # 检查请求是否成功
            if response.status_code == 200:
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                # 查找指定class为"RenderKeyPoints-list"的div元素
                author_div = soup.find('div', class_="Author-authorNameAndSocial")

                key_points_div = soup.find('div', class_='RenderKeyPoints-list')

                info_div = soup.find('div', class_='ArticleBody-articleBody')

                if author_div:
                    # 获取 Jeff Cox 的姓名
                    author_name = soup.find('a', class_='Author-authorName').text
                    print("Author Name:", author_name)

                # 打印div元素的内容
                if key_points_div:
                    res = key_points_div.get_text()
                    print("Key Points结果为：{}".format(res))
                    prompt = get_prompt(prompt="key")
                    # 在这里调用g4f
                    # key_point_analysis = call_g4f(result, prompt)
                    # print(key_point_analysis)
                else:
                    print("未找到文章的的Key Points。")

                if info_div:
                    info = info_div.get_text()
                    print("文章结果为：{}".format(info))
                    prompt = get_prompt(prompt="content")
                    # 在这里调用g4f
                    # info_analysis = call_g4f(info, prompt)
                    # print(info_analysis)
                else:
                    print("没有找到该文章的内容")
            else:
                print("无法获取页面内容，状态码：", response.status_code)


if __name__ == "__main__":
    fed_url = "https://www.cnbc.com/jeff-cox/"
    fed_div_class = "RiverCard-standardBreakerCard RiverCard-specialReportsRiver RiverCard-card"

    # 获取联邦新闻链接
    fed_news_links = get_fed_news_links(fed_url, fed_div_class)

    # 处理联邦新闻
    process_fed_news(fed_news_links, target_date=date(2023, 12, 1))

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key="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",
    )

    steam = call_gpt(client, messages)
