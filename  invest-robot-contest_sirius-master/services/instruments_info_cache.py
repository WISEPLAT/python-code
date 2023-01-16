from api_calls.get_info import get_shares
from utils.util import is_file_exists, read_dict_from_file, write_dict_to_file, pretty_dict

instruments_cache = {}
instruments_cache_filename = 'data/cache_instruments'


# Кэш инструментов. Зачитывается с сервера один раз и записывается в файл. Кэш можно сбросить запуском --reset-robot

def get_instruments_cache():
    return instruments_cache


def make_instrument_key(exchange, ticker):
    return exchange + '_' + ticker


def get_instrument_info(exchange, ticker):
    global instruments_cache
    return get_instrument_info_by_key(make_instrument_key(exchange, ticker))


def get_instrument_info_by_key(key):
    global instruments_cache
    return instruments_cache[key]


def init_instruments_cache():
    global instruments_cache

    if is_file_exists(instruments_cache_filename):
        instruments_cache = read_dict_from_file(instruments_cache_filename)
        return

    shares = get_shares()['instruments']

    instruments_cache = {}

    for instrument in shares:
        ticker = instrument['ticker']
        exchange = instrument['exchange']
        instruments_cache[make_instrument_key(exchange, ticker)] = {
            'ticker': instrument['ticker'],
            'exchange': instrument['exchange'],
            'figi': instrument['figi'],
            'min_lot': instrument['lot'],
            'currency': instrument['currency'].upper(),
            'class_code': instrument['classCode']
        }

    write_dict_to_file(instruments_cache_filename, instruments_cache)

