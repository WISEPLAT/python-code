import logging
import time
from datetime import timedelta

from api_calls.get_info import get_candles_by_figi
from services.instruments_info_cache import get_instrument_info
from utils.datetime_utils import date_minus_days, current_date, string_to_date
from utils.settings import settings
from utils.util import read_dict_from_file, write_dict_to_file, pretty_dict

# методы используются в режиме history_test

# тестовые даты старта и остановки. Определяются как самая ранняя/поздняя дата свечей при инициализации
# данных в init_history_test_data()
test_current_date = None
test_stop_date = None
poll_interval_minutes = int(settings()['TRADE']['poll_interval_minutes'])


def init_history_test_data():
    global test_current_date
    global test_stop_date
    res = read_dict_from_file('data/test_history')
    if res is None:
        return res

    for info in res:
        start_date = string_to_date(info['candles'][0]['time'])
        stop_date = string_to_date(info['candles'][-1]['time'])
        if test_current_date is None or start_date < test_current_date:
            test_current_date = start_date
        if test_stop_date is None or stop_date > test_stop_date:
            test_stop_date = stop_date

    return res


test_info = init_history_test_data()


def get_test_current_date():
    return test_current_date


#  сдвинуть тестовую дату на poll_interval
def get_next_test_current_date():
    global test_current_date
    test_current_date = test_current_date + timedelta(minutes=poll_interval_minutes)
    return test_current_date


def get_test_data(exchange, ticker):
    for instrument in test_info:
        if instrument['exchange'] == exchange and instrument['ticker'] == ticker:
            return instrument
    return None


# TODO speed up search
def test_get_candles_by_date(exchange, ticker, from_date_time_timestamp, to_date_time_timestamp):
    ticker_test_info = get_test_data(exchange, ticker)
    if ticker_test_info is None:
        return []

    ticker_candles = ticker_test_info['candles']
    res = []
    for candle in ticker_candles:
        candle_date = candle['datetime']
        if candle_date < from_date_time_timestamp:
            continue
        elif candle_date > to_date_time_timestamp:
            break
        res.append(candle)
    return res


# условие остановки при тестовом режиме
def test_get_stop():
    global test_stop_date
    return get_test_current_date() > test_stop_date


def prepare_history_file(days):
    instruments = read_dict_from_file('instruments_history_test')

    logging.info("Preparing history test for {} days for following instruments:\n{}"
                 .format(days, pretty_dict(instruments)))

    for instrument in instruments:
        instrument_info = get_instrument_info(instrument['exchange'], instrument['ticker'])
        figi = instrument_info['figi']
        candles = []

        for i in range(0, days):
            candles.extend(get_candles_by_figi(figi, date_minus_days(current_date(), days - i),
                                               date_minus_days(current_date(), days - i - 1),
                                               'CANDLE_INTERVAL_1_MIN')['candles'])
        for candle in candles:
            candle['datetime'] = string_to_date(candle['time']).timestamp()
        instrument['candles'] = candles
        logging.info("Candles for one day for instrument = {} {} has been prepared"
                     .format(instrument['exchange'], instrument['ticker']))

        time.sleep(2)  # to avoid rate limit break

    write_dict_to_file('data/test_history', instruments)

    logging.info("History file successfully prepared")
