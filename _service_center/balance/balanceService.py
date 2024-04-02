import okx.Account as Account
import json
from _service_center.account_okx import MyBalance, Data, Detail

config_file_path = '../../config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

apikey = config['apikey']
secretkey = config['secretkey']
passphrase = config['passphrase']

flag = "0"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get account balance
result = accountAPI.get_account_balance()

print(result)

# print(res["code"])
#
# print(res["data"])

balanceObject = MyBalance(**result)

# print(balanceObject.code)


balanceEth = accountAPI.get_account_balance("ETH")

balanceEthObj = MyBalance(**balanceEth)

balanceEthData = balanceEthObj.__getattribute__('data')[0]

balanceEthDataObj = Data(**balanceEthData)

balanceEthDetails = balanceEthDataObj.__getattribute__('details')[0]

balanceEthDetailsObj = Detail(**balanceEthDetails)

print(balanceEthDetailsObj)


