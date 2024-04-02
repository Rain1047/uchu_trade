balanceTotal = int(input("请输入总资产："))

print("总资产为：" + str(balanceTotal))

# 交易中的总金额
balanceInTrade = 0


# 未交易的金额
balanceLeft = 0

# 可以用于交易的金额 总金额的70% - 交易中的金额
balanceCanTrade = int(balanceTotal * 0.7 - balanceInTrade)

# 需要留出的金额 总金额的30% - 未交易的金额
balanceCanLeft = int(balanceCanTrade * 0.3 - balanceLeft)

# 交易BTC
balanceInBtc = 0

balanceCanTradeBtc = int(balanceCanTrade * 0.7 * 0.5 - balanceInBtc)

# 交易ETH
balanceInEth = 0

balanceCanTradeEth = int(balanceCanTrade * 0.7 * 0.5 - balanceInEth)


print("可用于交易Eth的金额：{0}".format(balanceCanTradeEth))

