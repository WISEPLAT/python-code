import logging
import time
import traceback

from api_calls.get_info import get_candles_by_figi
from services.account_info import has_enough_money
from services.history_test_data import test_get_candles_by_date, get_test_current_date, get_next_test_current_date
from services.instruments_info_cache import make_instrument_key, get_instrument_info_by_key
from services.trading_info import get_trading_info_for_key, save_trading_info
from strategy.buy_sell_utils import sell, buy
from strategy.calculate_utils import calc_profit_percent, add_prices_to_candles
from strategy.trade_signal import get_trade_signal
from utils.datetime_utils import current_date, string_to_date, date_minus_minutes
from utils.settings import settings


# отдельный торговый поток. Возможно, следует иметь по одному отдельному потоку на каждый инструмент торговли.

def get_candles(instrument_info, last_processed_date):
    if settings()['MAIN']['mode'] == 'history_test':
        exchange = instrument_info['exchange']
        ticker = instrument_info['ticker']
        return test_get_candles_by_date(exchange, ticker, last_processed_date.timestamp(),
                                        get_current_date().timestamp())
    elif settings()['MAIN']['mode'] == 'sandbox':
        return get_candles_by_figi(instrument_info['figi'], last_processed_date, get_current_date(),
                                   'CANDLE_INTERVAL_1_MIN')['candles']
    return None

# TODO take profit/stop loss вынести в trade_signal
def process_instrument(account_info, instrument, trading_info, last_processed_date):
    instrument_key = make_instrument_key(instrument['exchange'], instrument['ticker'])
    instrument_info = get_instrument_info_by_key(instrument_key)

    instrument_trading_info = get_trading_info_for_key(instrument_key, trading_info)
    has_share = instrument_trading_info['has_share']

    candles = get_candles(instrument_info, last_processed_date)
    candles = add_prices_to_candles(candles)

    if len(candles) == 0:
        return

    last_candle = candles[-1]
    last_price = last_candle['price']

    # May be take profit or stop loss
    if has_share:
        profit_percent = calc_profit_percent(last_price, instrument_trading_info['last_buy_price'])
        sell_reason = ''
        if profit_percent > float(settings()['TRADE']['take_profit_percent']):
            sell_reason = 'take_profit'
        elif profit_percent < -float(settings()['TRADE']['stop_loss_percent']):
            sell_reason = 'stop_loss'

        if sell_reason:
            do_sell(account_info, instrument_info, instrument_trading_info, candles, sell_reason)
        return

    signal = get_trade_signal(candles)

    if has_share:
        if signal == 'sell':
            do_sell(account_info, instrument_info, instrument_trading_info, candles, 'signal')
    else:
        if signal == 'buy':
            do_buy(account_info, instrument_info, instrument_trading_info, candles)


def do_buy(account_info, instrument_info, instrument_trading_info, candles):
    deal_result = buy(account_info, instrument_info, candles)
    if deal_result is None:
        return

    instrument_trading_info['has_share'] = True
    instrument_trading_info['last_buy_price'] = deal_result['price']

    instrument_trading_info['buy_count'] = instrument_trading_info['buy_count'] + 1
    instrument_trading_info['balance'] = instrument_trading_info['balance'] - \
                                         deal_result['deal_price'] - deal_result['commission']

    logging.info("{} buy, price = {} {} {}"
                 .format(instrument_info['ticker'], deal_result['deal_price'],
                         instrument_info['currency'], deal_result['datetime']))


def do_sell(account_info, instrument_info, instrument_trading_info, candles, reason):
    deal_result = sell(account_info, instrument_info, candles)
    if deal_result is None:
        return

    profit_percent = calc_profit_percent(deal_result['price'], instrument_trading_info['last_buy_price'])

    instrument_trading_info['has_share'] = False
    instrument_trading_info['last_buy_price'] = 0

    instrument_trading_info['sell_count'] = instrument_trading_info['sell_count'] + 1
    instrument_trading_info['balance'] = instrument_trading_info['balance'] + \
                                         deal_result['deal_price'] - deal_result['commission']

    logging.info("{} sell {}, price = {} {} profit_percent = {} {}"
                 .format(instrument_info['ticker'], reason, deal_result['deal_price'],
                         instrument_info['currency'], round(profit_percent, 2), deal_result['datetime']))


def get_current_date():
    if settings()['MAIN']['mode'] == 'history_test':
        return get_test_current_date()
    else:
        return current_date()


def is_time_to_process(last_processed_date, current_date, poll_interval_minutes):
    return (current_date - last_processed_date).total_seconds() >= poll_interval_minutes * 60


def start_robot_thread(account_info, trading_info, instruments, should_stop_callback):
    logging.info("Robot thread started")

    poll_interval_minutes = int(settings()['TRADE']['poll_interval_minutes'])

    if settings()['MAIN']['mode'] == 'history_test':
        last_processed_date = get_current_date()
    else:
        cur_date = get_current_date()
        if trading_info['last_processed_date'] is not None:
            last_processed_date = string_to_date(trading_info['last_processed_date'])
            if is_time_to_process(last_processed_date, cur_date, poll_interval_minutes):
                last_processed_date = date_minus_minutes(cur_date, poll_interval_minutes)
        else:
            last_processed_date = date_minus_minutes(current_date(), poll_interval_minutes)

    while not should_stop_callback():

        try:
            cur_date = get_current_date()

            if is_time_to_process(last_processed_date, cur_date, poll_interval_minutes):
                if settings()['MAIN']['mode'] != 'history_test':
                    logging.info("Processing instruments")
                if has_enough_money(account_info):
                    for instrument in instruments:
                        process_instrument(account_info, instrument, trading_info, last_processed_date)
                else:
                    logging.warning("Processing skipped. Robot will not trade until it will have enough money")
                last_processed_date = cur_date
                trading_info['last_processed_date'] = str(last_processed_date)

                if settings()['MAIN']['mode'] != 'history_test':
                    save_trading_info(trading_info)

            if settings()['MAIN']['mode'] == 'history_test':
                get_next_test_current_date()
            else:
                time.sleep(1)
        except Exception as ex:
            logging.error("Unexpected exception {}".format(ex))
            traceback.print_exc()
            time.sleep(10)

    logging.info("Robot thread finished, enter any command to exit")
