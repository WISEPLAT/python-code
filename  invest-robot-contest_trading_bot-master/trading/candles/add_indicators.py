from ta.trend import ema_indicator, macd, adx


'''
    Тут представлены все функции, которые позволяют добавить в DataFrame необходимые индикааторы
        для дальнейшего использования в анализе.
'''

'''
    Функция для добавления индикатора EMA
'''


def add_ema(df, window=7):

    df[f"ema_{window}"] = ema_indicator(close=df['close'], window=window)

    return df


'''
    Функция для добавления индикатора MACD
'''


def add_macd(df):

    df['macd'] = macd(close=df['close'])

    return df


'''
    Функция для добавления индикатора ADX
'''


def add_adx(df, window=14):

    df['adx'] = adx(close=df['close'], high=df['high'], low=df['low'], window=window)

    return df