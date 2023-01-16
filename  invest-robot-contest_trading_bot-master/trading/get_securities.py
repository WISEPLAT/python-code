from tinkoff.invest import Client
from config.personal_data import get_token
from trading.trade_help import quotation_to_float
import Levenshtein

"""

    Тут собраны все функции, которые позволяют получить FIGI по тикеру бумаги
    или тикер бумаги по FIGI
    
    Тинькофф использует для всех операций покупок/продаж FIGI, 
    при этом для человеческого восприятия удобнее использовать название компании.
    
    Например. Акции ВТБ:
    FIGI = "BBG004730ZJ9"
    Ticker = "VTBR"
    Name = "Банк ВТБ"

"""

'''
    Функция для получения названия бумаги по FIGI
'''


def security_name_by_figi(figi, user_id):
    with Client(get_token(user_id)) as client:

        try:
            security_name = client.instruments.get_instrument_by(id_type=1, id=figi).instrument.name
            return security_name
        except Exception as ex:
            print(ex)

    return 0


'''
    Функция для получения минимального шага цены по FIGI
'''


def security_incr_by_figi(figi, user_id):
    with Client(get_token(user_id)) as client:

        try:
            security_incr = quotation_to_float(
                client.instruments.get_instrument_by(id_type=1, id=figi).instrument.min_price_increment)
            return security_incr
        except Exception as ex:
            print(ex)

    return 0


"""
    Позволяет получить список ценных бумаг по названию или FIGI
"""


def security_by_figi(user_id, figi):
    with Client(get_token(user_id)) as client:
        try:
            security = client.instruments.get_instrument_by(id_type=1, id=figi).instrument
            return security
        except Exception as ex:
            print(ex)
    return security


"""
    Позволяет получить список ценных бумаг по названию или FIGI
"""


def get_security_list(user_id, name, security_type="share"):

    with Client(get_token(user_id)) as client:

        examples = []

        try:
            examples += [client.instruments.get_instrument_by(id_type=1, id=name).instrument]
            return examples
        except:

            if security_type == "share":
                security = client.instruments.shares()
            elif security_type == "bond":
                security = client.instruments.bonds()
            elif security_type == "etf":
                security = client.instruments.etfs()
            elif security_type == "future":
                security = client.instruments.futures()
            elif security_type == "currency":
                security = client.instruments.currencies()

            for i in security.instruments:
                if Levenshtein.distance(i.name.lower().replace(" ", ""), name.lower().replace(" ", "")) < len(
                        i.name) * 0.3:
                    examples += [i]
                elif Levenshtein.distance(i.name.lower().replace(" ", ""), name.lower().replace(" ", "")) < len(
                        i.name) * 0.7:
                    if name.lower() in i.name.lower():
                        examples += [i]

        return examples
