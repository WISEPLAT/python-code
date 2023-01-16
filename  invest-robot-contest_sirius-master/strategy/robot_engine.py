import logging
import threading

from services.account_info import prepare_account_info, has_enough_money
from services.history_test_data import test_get_stop
from services.trading_info import load_trading_info, print_trading_info, save_trading_info
from strategy.robot_thread import start_robot_thread
from utils.settings import settings
from utils.util import read_dict_from_file, pretty_dict

stop_thread = False


def should_stop_callback():
    if stop_thread:
        return True
    if settings()['MAIN']['mode'] == 'history_test':
        return test_get_stop()
    return False


# инструменты, по которым робот будет вести торговлю
def load_trading_instruments():
    instruments = None

    if settings()['MAIN']['mode'] == 'history_test':
        instruments = read_dict_from_file('instruments_history_test')
    elif settings()['MAIN']['mode'] == 'sandbox':
        instruments = read_dict_from_file('instruments_sandbox')
    elif settings()['MAIN']['mode'] == 'prod':
        instruments = read_dict_from_file('instruments_prod')

    return instruments


def start_trade():
    account_info = prepare_account_info()

    has_enough_money(account_info)

    trading_info = load_trading_info()
    logging.info("Trading info loaded = {}\n".format(pretty_dict(trading_info)))
    instruments = load_trading_instruments()
    logging.info("Trading instruments loaded = {}\n".format(pretty_dict(instruments)))

    robot_thread = threading.Thread(target=start_robot_thread,
                                    args=(account_info, trading_info, instruments, should_stop_callback))
    robot_thread.start()

    while robot_thread.is_alive():
        global stop_thread

        if settings()['MAIN']['mode'] != 'history_test':
            command = input('')
            if command in ['q', 'quit']:
                stop_thread = True
            elif command == 'trading_info':
                print_trading_info(trading_info)
            else:
                logging.warning("Unknown command '{}'".format(command))

    print_trading_info(trading_info)

