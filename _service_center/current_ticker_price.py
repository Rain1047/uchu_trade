import okx.MarketData as MarketData

flag = "0"  # 实盘:0 , 模拟盘：1


if __name__ == '__main__':

    marketDataAPI = MarketData.MarketAPI(flag=flag)

    # 获取单个产品行情信息
    result = marketDataAPI.get_ticker(
        instId="BTC-USDT-SWAP"
    )['data'][0]['last']

    print(result)

