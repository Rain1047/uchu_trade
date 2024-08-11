import requests
from datetime import datetime

def get_top_cryptos():
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

        # 提取前20个加密货币的信息
        top_cryptos = []
        for crypto in data:
            crypto_info = {
                'name': crypto['name'],
                'symbol': crypto['symbol'],
                'market_cap': crypto['market_cap'],
            }
            top_cryptos.append(crypto_info)

        return top_cryptos
    else:
        # 输出错误信息
        print(f"Error: {response.status_code}")
        return None

def get_crypto_price_data(crypto_id, start_date, end_date):
    # CoinGecko API endpoint for fetching historical price data
    api_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart/range"

    # 将日期转换为时间戳（Unix时间）
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_timestamp = int(datetime.now().timestamp())

    # 参数
    params = {
        'vs_currency': 'usd',  # 换算成美元
        'from': start_timestamp,
        'to': end_timestamp,
    }

    # 发送GET请求
    response = requests.get(api_url, params=params)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()

        # 提取价格数据
        prices = data.get('prices', [])

        # 计算涨幅、最低价格和最高价格
        if prices:
            start_price = prices[0][1]
            end_price = prices[-1][1]
            price_change = ((end_price - start_price) / start_price) * 100
            min_price = min(prices, key=lambda x: x[1])[1]
            max_price = max(prices, key=lambda x: x[1])[1]

            return {
                'price_change': price_change,
                'min_price': min_price,
                'max_price': max_price,
            }
        else:
            return None
    else:
        # 输出错误信息
        print(f"Error: {response.status_code}")
        return None

def get_top_cryptos_price_data(start_date, end_date):
    top_cryptos = get_top_cryptos()
    crypto_data = []

    for crypto in top_cryptos:
        crypto_id = get_crypto_id(crypto['symbol'])
        if crypto_id:
            price_data = get_crypto_price_data(crypto_id, start_date, end_date)
            if price_data:
                crypto_info = {
                    'name': crypto['name'],
                    'symbol': crypto['symbol'],
                    'price_change': price_data['price_change'],
                    'min_price': price_data['min_price'],
                    'max_price': price_data['max_price'],
                }
                crypto_data.append(crypto_info)

    return crypto_data

def get_crypto_id(crypto_symbol):
    # CoinGecko API endpoint for fetching list of cryptocurrencies
    api_url = "https://api.coingecko.com/api/v3/coins/list"

    # 发送GET请求
    response = requests.get(api_url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()

        # 查找加密货币的ID
        for crypto in data:
            if crypto['symbol'].lower() == crypto_symbol.lower():
                return crypto['id']

        print(f"未找到符号为 {crypto_symbol} 的加密货币。")
        return None
    else:
        # 输出错误信息
        print(f"Error: {response.status_code}")
        return None


if __name__ == "__main__":
    start_date = "2023-09-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    top_cryptos_data = get_top_cryptos_price_data(start_date, end_date)

    if top_cryptos_data:
        print(f"市值前20的加密货币从 {start_date} 到 {end_date} 的涨幅、最低价格和最高价格：")
        for i, crypto_data in enumerate(top_cryptos_data, start=1):
            print(f"{i}. {crypto_data['name']} ({crypto_data['symbol']}):")
            print(f"   涨幅: {crypto_data['price_change']:.2f}%")
            print(f"   最低价格: ${crypto_data['min_price']:.2f}")
            print(f"   最高价格: ${crypto_data['max_price']:.2f}")
            print()
    else:
        print("无法获取加密货币数据。")
