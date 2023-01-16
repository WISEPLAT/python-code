import logging

from api_calls.common_requests import make_api_request
from utils.datetime_utils import date_to_str

service_path = 'tinkoff.public.invest.api.contract.v1.InstrumentsService/'
market_path = 'tinkoff.public.invest.api.contract.v1.MarketDataService/'


def get_shares():
    res = make_api_request(service_path + 'Shares')
    logging.debug("Get shares done")
    return res


# get_share_by_ticker("SPBXM", "AMZN")
# get_share_by_ticker("TQBR", "SBER")
def get_share_by_ticker(class_code, ticker):
    res = make_api_request(service_path + 'ShareBy',
                           dict(idType="INSTRUMENT_ID_TYPE_TICKER", classCode=class_code, id=ticker))
    logging.debug("Get info for stock = {}, ticker = {}".format(class_code, ticker))
    return res


# intervals
# [ CANDLE_INTERVAL_UNSPECIFIED, CANDLE_INTERVAL_1_MIN, CANDLE_INTERVAL_5_MIN, CANDLE_INTERVAL_15_MIN,
# CANDLE_INTERVAL_HOUR, CANDLE_INTERVAL_DAY ]
def get_candles_by_figi(figi, from_datetime, to_datetime, interval):
    res = make_api_request(market_path + 'GetCandles',
                           {'figi': figi,
                            'from': date_to_str(from_datetime),
                            'to': date_to_str(to_datetime),
                            'interval': interval})
    logging.debug("Get candles done")
    return res

# Запрошенный интервал свечей	Допустимый период запроса
# CANDLE_INTERVAL_1_MIN	от 1 минут до 1 дня
# CANDLE_INTERVAL_5_MIN	от 5 минут до 1 дня
# CANDLE_INTERVAL_15_MIN	от 15 минут до 1 дня
# CANDLE_INTERVAL_HOUR	от 1 часа до 1 недели
# CANDLE_INTERVAL_DAY	от 1 дня до 1 года
