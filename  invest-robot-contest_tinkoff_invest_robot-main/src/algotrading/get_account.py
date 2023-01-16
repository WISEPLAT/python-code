from tinkoff.invest import GetMarginAttributesResponse
from tinkoff.invest import RequestError

from loguru import logger

from . import glossary, utils


def print_accounts(accounts):
    print(f"У вас счетов: {len(accounts)} ")
    accounts_id = []
    for account in accounts:
        accounts_id.append(account.id)
        print(account.id, " ".join(account.type._name_.split('_')[2:]), account.name,
              " ".join(account.status._name_.split('_')[2:]),
              account.opened_date.strftime("%Y-%m-%d")
              )

    return accounts_id


def get_users_info(client):
    user_info = client.users.get_info()
    users = {}
    users.update(user_info.__dict__)

    users['qualified_for_work_with'] = [glossary.qualified_for_work_with[qualified] for qualified in
                                        user_info.qualified_for_work_with]

    return users


def get_margin_attributes(client, account_id: int) -> GetMarginAttributesResponse:
    try:
        margin_attributes = client.users.get_margin_attributes(account_id=account_id)

    except RequestError as err:
        logger.debug(f"для счета {account_id}, {err.metadata.message}")
        return None

    return margin_attributes


def get_user_accounts(client):
    accounts = {}

    for account in client.users.get_accounts().accounts:
        accounts[account.id] = {}
        accounts[account.id]["account"] = {}
        accounts[account.id]["account"]['name'] = account.name
        accounts[account.id]["account"]['id'] = account.id
        accounts[account.id]["account"]['status'] = " ".join(account.status._name_.split('_')[2:])
        accounts[account.id]["account"]['opened_date'] = account.opened_date.strftime("%Y-%m-%d")
        accounts[account.id]["account"]['token_access_level'] = " ".join(account.access_level._name_.split('_')[3:])

        margin_attr = get_margin_attributes(client, account.id)
        accounts[account.id]["margin_attributes"] = {}
        if margin_attr:
            liquid_portfolio = f"{margin_attr.liquid_portfolio.units} {margin_attr.liquid_portfolio.currency}"
            starting_margin = f"{margin_attr.starting_margin.units} {margin_attr.starting_margin.currency}"
            minimal_margin = f"{margin_attr.minimal_margin.units} {margin_attr.minimal_margin.currency}"
            amount_of_missing_funds = f"{margin_attr.amount_of_missing_funds.units} {margin_attr.amount_of_missing_funds.currency}"

            accounts[account.id]["margin_attributes"]['liquid_portfolio'] = liquid_portfolio
            accounts[account.id]["margin_attributes"]['starting_margin'] = starting_margin
            accounts[account.id]["margin_attributes"]['minimal_margin'] = minimal_margin
            accounts[account.id]["margin_attributes"]['amount_of_missing_funds'] = amount_of_missing_funds

        else:
            accounts[account.id]["margin_attributes"]["status"] = "margin status is disabled"

    return accounts


def get_account(client):
    user_info = get_users_info(client)

    return user_info


def main():
    api_client = utils.api_client_configure()
    with api_client as client:
        user_info = get_account(client)
        user_info['accounts'] = get_user_accounts(client)

    return user_info


def test_connect():
    api_client = utils.api_client_configure()
    try:
        with api_client as client:
            get_account(client)

    except RequestError as err:
        logger.critical(err.metadata.message)
        raise err


if __name__ == "__main__":
    main()
