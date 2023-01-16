from tinkoff.invest import Client
from trading.trade_help import to_quotation
from config.personal_data import get_token, get_account
from tinkoff.invest import MoneyValue


def add_money_sandbox(user_id, sum, currency, account_id=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        units = to_quotation(float(sum)).units
        nano = to_quotation(float(sum)).nano

        pay_in = client.sandbox.sandbox_pay_in(
            account_id=account_id,
            amount=MoneyValue(units=units, nano=nano, currency=f"{currency}")
        )

    return pay_in
