import okx.PublicData as PublicData

flag = "0"  # 实盘:0 , 模拟盘：1


if __name__ == '__main__':
    publicDataAPI = PublicData.PublicAPI(flag=flag)
    # 张币转换
    result = publicDataAPI.get_convert_contract_coin(
        instId="BTC-USDT-SWAP",
        px="68000",
        sz="50000",
        unit="usds",
    )
    print(result['data'][0]['sz'])

    result = publicDataAPI.get_convert_contract_coin(
        instId="ETH-USDT-SWAP",
        px="3651",
        sz="50000",
        unit="usds",
    )
    print(result)

    result = publicDataAPI.get_convert_contract_coin(
        instId="SOL-USDT-SWAP",
        px="190",
        sz="50000",
        unit="usds",
    )
    print(result)

    result = publicDataAPI.get_convert_contract_coin(
        instId="AVAX-USDT-SWAP",
        px="57",
        sz="50000",
        unit="usds",
    )
    print(result)
