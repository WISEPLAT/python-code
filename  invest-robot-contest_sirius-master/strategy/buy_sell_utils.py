import logging
import time

from api_calls.prod_buy import prod_place_order, prod_get_order_state, prod_cancel_order
from api_calls.sandbox_buy import sandbox_place_order, sandbox_get_order_state, sandbox_cancel_order
from utils.datetime_utils import current_date
from utils.settings import settings
from utils.util import price_to_float

order_poll_interval = 1
seconds_to_wait_for_order_finished = 300


def make_deal_result(price, deal_price, commission, datetime):
    return {'price': price, 'deal_price': deal_price, 'commission': commission, 'datetime': datetime}


def buy(account_info, instrument_info, candles):
    try:
        if settings()['MAIN']['mode'] == 'history_test':
            return execute_history_test_order(instrument_info, candles)
        if settings()['MAIN']['mode'] == 'sandbox':
            return place_order_and_wait_for_finish(account_info, instrument_info, 'buy', True)
        if settings()['MAIN']['mode'] == 'prod':
            return place_order_and_wait_for_finish(account_info, instrument_info, 'buy', False)
    except Exception as ex:
        logging.error("Buy failed, account_info = {}, instrument_info = {}, exception = {}",
                      account_info, instrument_info, ex)
        return None


def sell(account_info, instrument_info, candles):
    try:
        if settings()['MAIN']['mode'] == 'history_test':
            return execute_history_test_order(instrument_info, candles)
        if settings()['MAIN']['mode'] == 'sandbox':
            return place_order_and_wait_for_finish(account_info, instrument_info, 'sell', True)
        if settings()['MAIN']['mode'] == 'prod':
            return place_order_and_wait_for_finish(account_info, instrument_info, 'sell', False)
    except Exception as ex:
        logging.error("Sell failed, account_info = {}, instrument_info = {}, exception = {}",
                      account_info, instrument_info, ex)
        return None


def execute_history_test_order(instrument_info, candles):
    last_candle = candles[-1]
    test_price = last_candle['price']

    min_lot = instrument_info['min_lot']

    deal_price = test_price * min_lot
    commission = 0.003 * deal_price
    return make_deal_result(test_price, deal_price, commission, last_candle['time'])


def place_order_and_wait_for_finish(account_info, instrument_info, deal_type, is_sandbox):
    account_id = account_info['account_id']

    if is_sandbox:
        order = sandbox_place_order(account_id, instrument_info['figi'], 1, deal_type)
    else:
        order = prod_place_order(account_id, instrument_info['figi'], 1, deal_type)

    order_id = order['orderId']
    order_state = wait_for_order_statuses(account_id, order_id,
                                          ['EXECUTION_REPORT_STATUS_FILL', 'EXECUTION_REPORT_STATUS_REJECTED'], is_sandbox)
    logging.info("Trying to make '{}' for instrument = {}".format(deal_type, instrument_info))

    if order_state['executionReportStatus'] == 'EXECUTION_REPORT_STATUS_FILL':
        price = price_to_float(order_state['executedOrderPrice']['units'], order_state['executedOrderPrice']['nano'])
        deal_price = price_to_float(order_state['executedOrderPrice']['units'],
                                    order_state['executedOrderPrice']['nano'])
        commission = price_to_float(order_state['executedCommission']['units'],
                                    order_state['executedCommission']['nano'])
        exec_datetime = current_date()

        logging.info(
            "Deal '{}' successfully finished, instrument = {}, price = {}, deal_price = {}, commission = {} datetime = {}"
            .format(deal_type, instrument_info, price, deal_price, commission, exec_datetime))

        return make_deal_result(price, deal_price, commission, exec_datetime)
    else:
        if is_sandbox:
            sandbox_cancel_order(account_id, order_id)
        else:
            prod_cancel_order(account_id, order_id)
        logging.error("Deal '{}' failed, instrument = {}, last order state = {}. Cancelling order"
                      .format(deal_type, instrument_info, order_state))
        return None


def wait_for_order_statuses(account_id, order_id, order_statuses, is_sandbox):
    start = time.time()
    order_state = None

    while True:
        time.sleep(order_poll_interval)
        if is_sandbox:
            order_state = sandbox_get_order_state(account_id, order_id)
        else:
            order_state = prod_get_order_state(account_id, order_id)

        logging.debug("Last order state = {}".format(order_state))
        order_status = order_state['executionReportStatus']
        if order_status in order_statuses:
            break
        seconds_elapsed = time.time() - start
        if seconds_elapsed > seconds_to_wait_for_order_finished:
            break

    return order_state
