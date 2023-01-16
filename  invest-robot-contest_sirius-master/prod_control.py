from api_calls.get_info import get_share_by_ticker
from api_calls.prod_account import *
from services.instruments_info_cache import get_instrument_info
from strategy.buy_sell_utils import place_order_and_wait_for_finish


def prod_control():
    help_str = """
Вспомогательный режим для управления prod-аккаунтом.
В примерах - 2000012345 - это account_id, который можно получить с помощью
команды info
Основные команды (вводить без кавычек):
'info' - вывести информацию по аккаунту
'portfolio 2000012345' - вывести подробное портфолио по счёту
'positions 2000012345' - вывести список позиций по счёту
'buy 2000012345 MOEX ORUP' - купить акцию ORUP на бирже MOEX
'sell 2000012345 SPB VEON' - продать акцию VEON на бирже SPB
'q' или 'quit' - выход
"""
    logging.info(help_str)

    while True:
        line = input('')
        if len(line) == 0:
            continue
        if line.lower() in ['q', 'quit']:
            break
        else:
            do_operation(line)


def do_operation(line):
    command = line.split()[0]
    args = line.split()[1:]

    if command == 'info':
        logging.info("Prod accounts = {}\n".format(pretty_dict(get_prod_accounts())))
    elif command == 'portfolio':
        logging.info("Prod portfolio = {}\n".format(pretty_dict(get_prod_portfolio(args[0]))))
    elif command == 'positions':
        logging.info("Prod positions = {}\n".format(pretty_dict(get_prod_positions(args[0]))))
    elif command == 'buy':
        do_operation_deal(account_id=args[0], exchange=args[1], ticker=args[2], deal_type=command)
    elif command == 'sell':
        do_operation_deal(account_id=args[0], exchange=args[1], ticker=args[2], deal_type=command)
    else:
        logging.warning("Unknown command '{}'".format(command))


def do_operation_deal(account_id, exchange, ticker, deal_type):
    instrument_info = get_instrument_info(exchange, ticker)
    place_order_and_wait_for_finish({'account_id': account_id}, instrument_info, deal_type, False)

