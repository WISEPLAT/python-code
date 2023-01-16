from datetime import datetime

from tinkoff.invest.utils import now


def is_open_exchange():
    # условно биржа работает до 18мск
    # todo получать из api
    close_time = now().replace(hour=16, minute=0, second=0, microsecond=0)
    return now() < close_time


def is_open_orders(time: datetime) -> bool:
    # доступно открытие позиций до 18мск
    available_time = time.replace(hour=15, minute=0, second=0, microsecond=0)
    return time < available_time


def is_premarket_time(time: datetime) -> bool:
    # пропускаю анализ премаркета
    available_time = time.replace(hour=7, minute=0, second=0, microsecond=0)
    return time < available_time
