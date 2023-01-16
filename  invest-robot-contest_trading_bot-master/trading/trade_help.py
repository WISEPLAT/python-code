from config.personal_data import get_token, get_account, get_account_type
import math
from tinkoff.invest import Client, Quotation, CandleInterval
from datetime import datetime, timedelta
from pycbrf.toolbox import ExchangeRates

"""

    Тут представлены все небольшие вспомогательные функции

"""

'''
    Функция для расчёта полной стоимости актива / общего количества средств
    Тинькофф возвращает стоимость в units и nano
    units - целая часть
    nano - дробная (9 знаков после запятой)
'''


def quotation_to_float(quotation: Quotation):
    sum = quotation.units + (quotation.nano * 1e-9)
    return sum


'''
    Функция для перевода дробного числа в Quotation
    Тинькофф получает стоимость в units и nano
    units - целая часть
    nano - дробная (9 знаков после запятой)
'''


def to_quotation(price):
    quotation = Quotation()
    quotation.units = int(math.modf(price)[1])
    quotation.nano = int(round(math.modf(price)[0] * 1e9))
    return quotation


'''
    Позволяет узнать количество бумаг в одном лоте по FIGI
'''


def in_lot_figi(figi, user_id):
    with Client(get_token(user_id)) as client:
        in_lot = client.instruments.get_instrument_by(id_type=1, id=figi).instrument.lot

    return int(in_lot)


'''
    Позволяет узнать, есть ли такой инструмент в портфеле
    Сравнение идёт по FIGI
'''


def is_in_portfolio(figi, user_id, account_id="", account_type=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            portfolio = client.sandbox.get_sandbox_portfolio(account_id=account_id)
        else:
            portfolio = client.operations.get_portfolio(account_id=account_id)
        for i in portfolio.positions:
            if i.figi == figi:
                return True

    return False


'''
    Функция для получения средней цены акции по свече

    В API Tinkoff нет функции, которая позволит узнать стоимость бумаги по FIGI
    По этой причине было решено получить свечки за неделю и взять последнюю доступную.
    Такое решение связано с тем, что торги не проходят в выходные дни, поэтому наилучшим решением будет выбрать
        большой интервал времени для избежания ошибок.  
'''


def get_price_figi(figi, user_id):
    with Client(get_token(user_id)) as client:
        try:
            candle = client.market_data.get_candles(
                figi=figi,
                from_=datetime.utcnow() - timedelta(days=7),
                to=datetime.utcnow(),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR)
    # Выбираем последнюю доступную свечку
    # Получаем среднюю стоимость бумаги путём складывания самой высокой и самой низкой цен
            average_price = ((quotation_to_float(candle.candles[-1].high) + quotation_to_float(candle.candles[-1].low)) / 2)
            return average_price
        except:
            return 0.0


'''
    Функция для получения знака валюты
'''


def get_currency_sing(currency):
    if currency == "try":
        sign = "₺"
    elif currency == "eur":
        sign = "€"
    elif currency == "kzt":
        sign = "₸"
    elif currency == "byn":
        sign = "Br"
    elif currency == "hkd":
        sign = "HK$"
    elif currency == "cny":
        sign = "¥"
    elif currency == "rub":
        sign = "₽"
    elif currency == "usd":
        sign = "$"
    elif currency == "jpy":
        sign = "¥"
    elif currency == "chf":
        sign = "₣"
    elif currency == "gbp":
        sign = "£"
    else:
        sign = currency

    return sign


'''
    Функция для получения курса валюты по отношению к рублю
    Используется библиотека ЦБ РФ
'''


def get_exchange_rate(currency):
    rates = ExchangeRates()
    exchange = rates[f'{currency.upper()}']

    if exchange is not None:
        exchange_rate = exchange.rate
    elif currency.upper() == "RUB":
        exchange_rate = 1
    else:
        exchange_rate = 0

    return float(exchange_rate)
