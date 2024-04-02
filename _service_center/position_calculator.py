import okx.PublicData as PublicData

flag = "0"  # 实盘:0 , 模拟盘：1

publicDataAPI = PublicData.PublicAPI(flag=flag)


if __name__ == '__main__':

    # 获取当前比特币价格
    result = publicDataAPI.get_ticker(instId="BTC-USDT")

    # 打印结果
    print(result)
