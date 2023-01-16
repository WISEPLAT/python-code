import tinkoff.invest as ti
import pandas as pd
from datetime import datetime, timedelta
from ta.momentum import stoch, stoch_signal


CONTRACT_PREFIX = 'tinkoff.public.invest.api.contract.v1.'
INSTRUMENT_TICKER = 'GAZP'
WINDOW = 14
SMOOTH_WINDOW = 3


# Преобразование цены (https://azzrael.ru/api-v2-tinkoff-invest-get-candles-python)
def convert_price(p):
    return p.units + p.nano / 1e9


# Сохранение свеч в датафрейм (https://azzrael.ru/api-v2-tinkoff-invest-get-candles-python)
def create_df(candles: [ti.HistoricCandle]):
    df = pd.DataFrame([{
        'time': c.time,
        'volume': c.volume,
        'open': convert_price(c.open),
        'close': convert_price(c.close),
        'high': convert_price(c.high),
        'low': convert_price(c.low),
    } for c in candles])
    return df


def create_df_from_stream(c):
    df = pd.DataFrame({
        'time': [c.time],
        'volume': [c.volume],
        'open': [convert_price(c.open)],
        'close': [convert_price(c.close)],
        'high': [convert_price(c.high)],
        'low': [convert_price(c.low)]
    })
    return df


# Получение FIGI для акций на Мосбирже
def get_shares_figi(cl, sharesticker):
    result = cl.instruments.share_by(id_type=ti.InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code='TQBR',
                                     id=sharesticker)
    return result.instrument.figi


def get_shares_lot_size(cl, sharesticker):
    result = cl.instruments.share_by(id_type=ti.InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code='TQBR',
                                     id=sharesticker)
    return result.instrument.lot


def recalculate_time_series(df1, df2):
    del df1['%K']
    del df1['%D']
    result = pd.concat([df1, df2])
    result.sort_values(by='time', inplace=True)
    result = result.reset_index(drop=True)
    result['%K'] = stoch(result['high'], result['low'], result['close'], window=WINDOW, smooth_window=SMOOTH_WINDOW,
                         fillna=True)
    result['%D'] = stoch_signal(result['high'], result['low'], result['close'], window=WINDOW,
                                smooth_window=SMOOTH_WINDOW, fillna=True)
    # print(result.tail())
    return result


def get_sandbox_account_id(cl):
    accounts = cl.sandbox.get_sandbox_accounts()
    if len(accounts.accounts) > 0:
        result = accounts.accounts[0].id
        print(cl.sandbox.get_sandbox_positions(account_id=result))
        # cl.sandbox.close_sandbox_account(account_id=result)
    else:
        acc = cl.sandbox.open_sandbox_account()
        result = acc.account_id
        cl.sandbox.sandbox_pay_in(account_id=result, amount=ti.MoneyValue(currency='rub', units=10000, nano=0))
        print(cl.sandbox.get_sandbox_positions(account_id=result))
    return result


def get_time_series(cl, figi):
    starttime = datetime.now() - timedelta(days=1)
    finishtime = datetime.now()
    result = pd.DataFrame(data=None, columns=['time', 'volume', 'open', 'close', 'high', 'low'])
    while result.shape[0] < 1000:
        historiccandles = cl.market_data.get_candles(figi=figi, from_=starttime, to=finishtime,
                                                     interval=ti.CandleInterval.CANDLE_INTERVAL_5_MIN)
        tempdf = create_df(historiccandles.candles)
        result = pd.concat([result, tempdf])
        starttime = starttime - timedelta(days=1)
        finishtime = finishtime - timedelta(days=1)
    result.sort_values(by='time', inplace=True)
    result = result.reset_index(drop=True)
    result['%K'] = stoch(result['high'], result['low'], result['close'], window=WINDOW, smooth_window=SMOOTH_WINDOW,
                         fillna=True)
    result['%D'] = stoch_signal(result['high'], result['low'], result['close'], window=WINDOW,
                                smooth_window=SMOOTH_WINDOW, fillna=True)
    return result


def get_account_id(cl):
    result = 0
    accounts = cl.users.get_accounts()
    if len(accounts.accounts) > 0:
        for account in accounts.accounts:
            if account.access_level == ti.AccessLevel.ACCOUNT_ACCESS_LEVEL_FULL_ACCESS:
                response = cl.operations.get_positions(account_id=account.id)
                if response.money[0].units > 0:
                    result = account.id
    if result == 0:
        print('Нет аккаунтов с полным доступом или ненулевым балансом')
    return result
