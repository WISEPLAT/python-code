from intro.quotation_dt import quotation_count
from datetime import datetime, timedelta
from pathlib import Path
import tinkoff.invest
import intro.basek
import intro.accid
import pandas as pd
import time
import pandas_ta as ta

# Здесь запросы токена и id из stub файлов, и самого клиента из библиотеки Тинькофф
TOKEN = intro.basek.TINKOFF_INVEST_DOG_NEW
SDK_client = tinkoff.invest.Client(TOKEN)
User_acc_ID = intro.accid.ACC_ID

# Здесь переменные по которым будет производиться запрос свечей (Figi инструмента,
# интервал данных и месяц, а так же числа за который нужны данные.
# Эти значения выбираем вручную из полученного списка инструментов
cti_future = 'FUTBR0722000'
tf = tinkoff.invest.CandleInterval.CANDLE_INTERVAL_5_MIN
start_date = datetime.fromisoformat('2022-04-23T10:00:00')  # time from 10 a.m. UTC+3 format: '2022-04-25T13:00:00'
end_date = datetime.fromisoformat('2022-05-25T19:00:00')  # time to 7 p.m. UTC+3 format: '2022-04-25T13:00:00'


# Функция получения данных свечей по инструменту
def current_trade_instrument_candles(cti_figi, interval):
    try:
        with SDK_client as client:
            period = datetime.date(end_date) - datetime.date(start_date)
            period_days = period.days

            for i in range(0, period_days):
                current_date = start_date + timedelta(i)
                start = [current_date.year, current_date.month, current_date.day, start_date.hour, start_date.minute]
                end = [current_date.year, current_date.month, current_date.day, end_date.hour, end_date.minute]
                cti_candles = client.market_data.get_candles(
                    figi=cti_figi,
                    from_=datetime(start[0], start[1], start[2], start[3], start[4]),
                    to=datetime(end[0], end[1], end[2], end[3], end[4]),
                    interval=interval
                )
                # Обработка запроса по форме
                candle_df = create_candle_df(cti_candles.candles)
                if candle_df.empty:
                    continue
                else:
                    # Добавление индикаторов
                    candle_df['ema'] = ta.ema(candle_df['close'], 10)
                    candle_df['ma'] = ta.sma(candle_df['close'], lenght=10)
                    # Запись полученных данных в табличку
                    # указать название файла соответствующее инструменту
                    filepath = Path('csv_files/instrument_name.csv')
                    df = pd.DataFrame(candle_df)
                    print(df.dtypes)
                    df.to_csv(filepath, mode='a')
                    time.sleep(0.1)
                    print('Record ', i, ' complete')

            df_check = pd.read_csv('csv_files/instrument_name.csv')
            # Убираем пропуски значений
            df_check.dropna(inplace=True)
            # Убираем повторения названий из выгрузки
            df_check.drop_duplicates(subset=['time', 'volume', 'open', 'close', 'high', 'low'],
                                     inplace=True
                                     )
            df_check.drop(columns=['Unnamed: 0'], inplace=True)
            print(df_check.dtypes)
            df = df_check.convert_dtypes(infer_objects=True)
            # Запись полученных данных в табличку
            # указать название файла соответствующее инструменту
            filepath = Path('csv_files/instrument_name.csv')
            print(df.dtypes)
            df.to_csv(filepath, mode='w')

            return candle_df
    except tinkoff.invest.RequestError as e:
        print(str(e))


# Форма для обработки полученных данных
def create_candle_df(candles: [tinkoff.invest.HistoricCandle]):
    candle_df = pd.DataFrame([{
        'time': pd.Timestamp(c.time),
        'volume': c.volume,
        'open': quotation_count(c.open),
        'close': quotation_count(c.close),
        'high': quotation_count(c.high),
        'low': quotation_count(c.low),
    } for c in candles])
    return candle_df


ctic = current_trade_instrument_candles(cti_future, tf)
