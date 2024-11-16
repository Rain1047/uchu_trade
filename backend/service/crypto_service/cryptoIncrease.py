import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

def get_top_cryptos_symbols():
    # CoinGecko API endpoint for fetching cryptocurrency data
    api_url = "https://api.coingecko.com/api/v3/coins/markets"

    # 参数
    params = {
        'vs_currency': 'usd',  # 换算成美元
        'order': 'market_cap_desc',  # 按市值降序排列
        'per_page': 20,  # 获取前20个
        'page': 1,  # 第一页
        'sparkline': False,  # 不包含价格走势
    }

    # 发送GET请求
    response = requests.get(api_url, params=params)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()

        # 提取前20个加密货币的符号
        top_cryptos_symbols = [crypto['symbol'] for crypto in data]

        return top_cryptos_symbols
    else:
        # 输出错误信息
        print(f"Error: {response.status_code}")
        return None


def convert_to_yfinance_format(symbol):
    # 将符号格式化为yfinance可识别的格式（Symbol-USD）
    return f"{symbol}-USD"


def get_crypto_price_data(symbol):
    # 使用yfinance获取加密货币价格数据
    crypto_data = yf.download(symbol, start="2023-09-01", end=datetime.now().strftime("%Y-%m-%d"))

    return crypto_data


def export_to_excel(results, filename='crypto_data.xlsx'):

    # 创建DataFrame
    df = pd.DataFrame(results)

    # 导出到Excel
    df.to_excel(filename, index=False)
    print(f"数据已导出到 {filename}。")


if __name__ == "__main__":
    # 获取市值前20的加密货币的符号列表
    top_cryptos_symbols = get_top_cryptos_symbols()

    if top_cryptos_symbols:
        print("市值前20的加密货币的符号列表：")
        print(top_cryptos_symbols)
        print()

        # 获取价格数据并计算涨幅、最低价格和最高价格
        results = []

        for symbol in top_cryptos_symbols:
            yfinance_symbol = convert_to_yfinance_format(symbol)
            crypto_price_data = get_crypto_price_data(yfinance_symbol)

            if not crypto_price_data.empty:
                start_price = crypto_price_data['Close'].iloc[0]
                end_price = crypto_price_data['Close'].iloc[-1]
                price_change = ((end_price - start_price) / start_price) * 100
                min_price = crypto_price_data['Low'].min()
                max_price = crypto_price_data['High'].max()

                results.append({
                    'Symbol': yfinance_symbol,
                    '涨幅': price_change,
                    '最低价格': min_price,
                    '最高价格': max_price,
                })
            else:
                print(f"无法获取 {yfinance_symbol} 的价格数据。")

        # 导出到Excel文件
        timemiles = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = 'crypto_data_{}.xlsx'.format(timemiles)
        export_to_excel(results, filename=filename)

    else:
        print("无法获取加密货币符号列表。")
