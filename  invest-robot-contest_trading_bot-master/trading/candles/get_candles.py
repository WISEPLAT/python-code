from tinkoff.invest import Client, CandleInterval
from trading import trade_help
from config.personal_data import get_token
from datetime import datetime, timedelta
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt

"""
    Тут представлены функции для получения свечей различных интервалов
"""

'''
    Функция для получения часовых свечей за неделю
    
    API Tinkoff позволяет получить часовые свечи только за неделю.
    Для оптимизации когда было решено ввести переменную week, которая будет прибавлять/убавлять
        необходимое количество недель 
'''


def get_candles_hour(figi, user_id, week=0):
    with Client(get_token(user_id)) as client:
        candles = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(days=7 + 7 * week),
            to=datetime.utcnow() - timedelta(days=7 * week),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR
        )

    return candles


'''
    Функция для получения минутных свечей за час
'''


def get_candles_1_min(figi, user_id):
    with Client(get_token(user_id)) as client:
        candles = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(hours=24),
            to=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN
        )

        return candles


'''
    Функция для получения 5 минутных свечей за час
'''


def get_candles_5_min(figi, user_id):
    with Client(get_token(user_id)) as client:
        candles = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(hours=24),
            to=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_5_MIN
        )

        return candles


'''
    Функция для получения 15 минутных свечей за час
'''


def get_candles_15_min(figi, user_id, days=0):
    with Client(get_token(user_id)) as client:
        candles = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(hours=24 + 24 * days),
            to=datetime.utcnow() - timedelta(hours=24 * days),
            interval=CandleInterval.CANDLE_INTERVAL_15_MIN
        )

        return candles


'''
    Функция для получения дневных свечей за год
'''


def get_candles_day(figi, user_id):
    with Client(get_token(user_id)) as client:
        candles = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(days=365),
            to=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_DAY
        )

        return candles


'''
    Функция для перевода свечи в ДатаФрейм
    
    Было решено отформатировать формат времени, для более красивого оформления графика
'''


def get_candles_df(candles):
    candle_df = DataFrame([
        {
            'time': i.time,
            'time_graph': i.time.strftime('%d.%m.%Y'),
            'hour_graph': i.time.strftime('%H:%M'),  # Будет использоваться для построения plot
            'orders': i.volume,
            'open': trade_help.quotation_to_float(i.open),
            'close': trade_help.quotation_to_float(i.close),
            'high': trade_help.quotation_to_float(i.high),
            'low': trade_help.quotation_to_float(i.low),
        } for i in candles.candles

    ])

    return candle_df


'''
    Функция для построения часового графика
'''


def create_hour_graph(figi, user_id, week=0, save=True):
    candle_df = DataFrame()

    for i in range(week, -1, -1):
        c = get_candles_hour(figi, user_id, i)
        df = get_candles_df(c)
        candle_df = pd.concat([candle_df, df], ignore_index=True)

    if save:
        plt.savefig(f"img/graph.png")

    return candle_df


def create_15_min_graph(figi, user_id, days=0, save=True):
    candle_df = DataFrame()

    for i in range(days, -1, -1):
        c = get_candles_15_min(figi, user_id, i)
        df = get_candles_df(c)
        candle_df = pd.concat([candle_df, df], ignore_index=True)

    if save:
        plt.savefig(f"img/graph.png")

    return candle_df
