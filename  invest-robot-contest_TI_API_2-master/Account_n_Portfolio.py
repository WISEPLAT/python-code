import tinkoff.invest
import intro.basek
import intro.accid

TOKEN = intro.basek.TINKOFF_INVEST_DOG_NEW
SDK = tinkoff.invest.Client(TOKEN)
User_acc_ID = intro.accid.ACC_ID

# Для полученния ID
def get_account_info():
    with SDK as client:
        gai = client.users.get_accounts()
    print(gai)


get_account_info()

# Для получения Портфеля
def show_portfolio():
    with SDK as client:
        portfel = client.operations.get_portfolio(account_id=User_acc_ID)
        print(portfel)

    return

# show_portfolio()

