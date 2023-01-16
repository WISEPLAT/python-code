import logging

from services.instruments_info_cache import get_instrument_info_by_key
from utils.util import read_dict_from_file, write_dict_to_file, pretty_dict


# trading_info - результаты торговли по каждому инструменту. сохраняется в файл при завершении работы робота
# Пример элемента
# "MOEX_MTLR": {
#     "buy_count": 0,
#     "sell_count": 0,
#     "balance": 0,
#     "last_buy_price": 0,
#     "has_share": false
# }
# Когда робот покупает он увеличивает счётчик buy_count, запоминает последнюю цену покупки, устанавливает has_share=True.
# Баланс при этом уменьшается на стоимость покупки
# Когда робот продаёт, он увеличивает счётчик sell_count, устанавливает has_share=False.
# Баланс при этом уменьшается увеличивается на стоимость продажи
# Когда мы считаем примерный финансовый результат, если у робота на руках есть акция, то учитывается последняя цена покупки
###

def load_trading_info():
    res = read_dict_from_file('data/trading_info')
    if res is None:
        return {'results': {}, 'last_processed_date': None}
    else:
        return res


def save_trading_info(trading_info):
    write_dict_to_file('data/trading_info', trading_info)


def print_trading_info(trading_info):
    money = {'USD': 0, "RUB": 0}

    results = trading_info['results'].copy()

    for result_key in results:
        result = results[result_key]
        instrument_info = get_instrument_info_by_key(result_key)
        currency = instrument_info['currency']

        if result['has_share']:
            price = 1 * instrument_info['min_lot'] * result['last_buy_price']  # TODO 1 - replace with lots to buy
            result['balance'] = result['balance'] + price

        money[currency] = money[currency] + result['balance']

    logging.info('Finance results per instrument:\n{}'.format(pretty_dict(results)))
    logging.info('Finance result:\n{}'.format(pretty_dict(money)))


def get_trading_info_for_key(key, trading_info):
    results = trading_info['results']

    results.setdefault(key, {'buy_count': 0, 'sell_count': 0, 'balance': 0, 'last_buy_price': 0, 'has_share': False})
    return results[key]
