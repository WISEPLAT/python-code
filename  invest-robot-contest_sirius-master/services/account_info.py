import logging

from api_calls.prod_account import get_prod_accounts, get_prod_positions
from api_calls.sandbox_account import get_sandbox_accounts, get_sandbox_portfolio, get_sandbox_positions
from utils.settings import settings
from utils.util import price_to_float


# управление счётом. если не удалось загрузить - это fatal, завершаем программу
# если у пользователя несколько счетов, выбирается первый
# TODO - добавить в settings выбор счёта

def create_account_info(account_id):
    return {'account_id': account_id}


def prepare_account_info():
    account_info = None
    try:
        if settings()['MAIN']['mode'] == 'history_test':
            account_info = create_account_info(0)
        elif settings()['MAIN']['mode'] == 'sandbox':
            account_info = get_account_info(True)
        elif settings()['MAIN']['mode'] == 'prod':
            account_info = get_account_info(False)
    except:
        pass
    finally:
        if account_info is None:
            logging.fatal("Failed to load account info. May be you should check tokens.")
            quit(-1)
        else:
            logging.info("Account info loaded = {}".format(account_info))
        return account_info


def get_account_info(is_sandbox):
    if is_sandbox:
        accounts = get_sandbox_accounts()['accounts']
    else:
        accounts = get_prod_accounts()['accounts']

    if len(accounts) == 0:
        logging.warning("No accounts found!")
        return None
    elif len(accounts) != 1:
        logging.warning("More than 1 account. Accounts = {}. Robot will trade on the first one = {}"
                        .format(accounts, accounts[0]))

    account_id = accounts[0]['id']
    res = create_account_info(account_id)
    return res


def has_enough_money(account_info):
    positions = None
    if settings()['MAIN']['mode'] == 'history_test':
        return True
    elif settings()['MAIN']['mode'] == 'sandbox':
        positions = get_sandbox_positions(account_info['account_id'])
    elif settings()['MAIN']['mode'] == 'prod':
        positions = get_prod_positions(account_info['account_id'])

    min_usd = float(settings()['TRADE']['min_usd'])
    min_rub = float(settings()['TRADE']['min_rub'])

    current_usd = 0
    current_rub = 0

    for currency_positions in positions['money']:
        if currency_positions['currency'] == 'rub':
            current_rub = price_to_float(currency_positions['units'], currency_positions['nano'])
        elif currency_positions['currency'] == 'usd':
            current_usd = price_to_float(currency_positions['units'], currency_positions['nano'])

    if current_usd >= min_usd and current_rub >= min_rub:
        logging.debug("Current money usd = {}, rub = {}".format(current_usd, current_rub))
        return True
    else:
        logging.warning("Robot has not enough money, usd = {}, rub = {}. "
                        "Minimum settings: usd = {}, rub = {}"
                        .format(current_usd, current_rub, min_usd, min_rub))
        return False
