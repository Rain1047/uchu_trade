from backend.service.okx_api.okx_main_api import OKXAPIWrapper

if __name__ == '__main__':
    okx = OKXAPIWrapper()
    account = okx.account
    print(account.get_account_balance())

