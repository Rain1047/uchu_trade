from backend.data_center.data_object.dao.account_balance import AccountBalance
from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper

if __name__ == '__main__':
    okx = OKXAPIWrapper()
    account = okx.account
    response = account.get_account_balance()
    # AccountBalance.insert_or_update(response)
    print(len(AccountBalance.list_all()))
