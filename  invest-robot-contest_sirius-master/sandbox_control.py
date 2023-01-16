import logging

from api_calls.get_info import get_share_by_ticker
from api_calls.sandbox_account import *
from services.instruments_info_cache import get_instrument_info
from strategy.buy_sell_utils import place_order_and_wait_for_finish


def sandbox_control():
    help_str = """
Вспомогательный режим для управления sandbox-аккаунтом.
В примерах - 1eb65a36-8ecb-4bd8-b186-056547277f18 - это account_id счёта, который можно получить с помощью
команды info
Основные команды (вводить без кавычек):
'open_account' - открыть новый sandbox-счёт
'close_account 1eb65a36-8ecb-4bd8-b186-056547277f18' - закрыть sandbox-счёт
'info' - вывести информацию по аккаунту
'portfolio 1eb65a36-8ecb-4bd8-b186-056547277f18' - вывести портфолио по счёту
'positions 1eb65a36-8ecb-4bd8-b186-056547277f18' - вывести список позиций по счёту
'buy 1eb65a36-8ecb-4bd8-b186-056547277f18 MOEX ORUP' - купить акцию ORUP на бирже MOEX
'sell 1eb65a36-8ecb-4bd8-b186-056547277f18 SPB VEON' - продать акцию VEON на бирже SPB
'pay 1eb65a36-8ecb-4bd8-b186-056547277f18 USD 10000 35' - пополнить счёт на 10000 долларов и 35 центов
'pay 1eb65a36-8ecb-4bd8-b186-056547277f18 RUB 29999 0' - пополнить счёт на 29999 рублей
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
        logging.info("Sandbox accounts = {}\n".format(pretty_dict(get_sandbox_accounts())))
    elif command == 'portfolio':
        logging.info("Sandbox portfolio = {}\n".format(pretty_dict(get_sandbox_portfolio(args[0]))))
    elif command == 'positions':
        logging.info("Sandbox positions = {}\n".format(pretty_dict(get_sandbox_positions(args[0]))))
    elif command == 'close_account':
        logging.info("Sandbox close account = {}\n".format(pretty_dict(close_sandbox_account(args[0]))))
    elif command == 'open_account':
        logging.info("Sandbox open account = {}\n".format(pretty_dict(open_sandbox_account())))
    elif command == 'pay':
        logging.info("Sandbox pay for account = {}\n".format(
            pretty_dict(pay_sandbox_account(account_id=args[0], currency=args[1], units=args[2], nano=args[3]))))
    elif command == 'buy':
        do_operation_deal(account_id=args[0], exchange=args[1], ticker=args[2], deal_type=command)
    elif command == 'sell':
        do_operation_deal(account_id=args[0], exchange=args[1], ticker=args[2], deal_type=command)
    else:
        logging.warning("Unknown command '{}'".format(command))


def do_operation_deal(account_id, exchange, ticker, deal_type):
    instrument_info = get_instrument_info(exchange, ticker)
    place_order_and_wait_for_finish({'account_id': account_id}, instrument_info, deal_type, True)
