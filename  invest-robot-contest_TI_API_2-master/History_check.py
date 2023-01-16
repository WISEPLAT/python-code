# Этот файл заточен под работу с фьючерсами, для акций нужно изменить параметры.
# Плюс сейчас не хавтает аналитической части,
# она происходит уже в самой табдице (Посредством Google Sheets например).
import datetime
import math

import pandas as pd
# import matplotlib.pyplot as plt
import tinkoff.invest
import intro.basek
import intro.accid
from intro.quotation_dt import quotation_count

dtypes_dic = {'time': str,
              'volume': int,
              'open': float,
              'close': float,
              'high': float,
              'low': float,
              'ma': float,
              'ema': float
              }

# Часть для обработки файла с данными
hist_candles_inst = pd.read_csv('csv_files/brent092022_7-8mnth.csv', dtype=dtypes_dic)

# Здесь запросы токена и id из stub файлов, и самого клиента из библиотеки Тинькофф
TOKEN = intro.basek.TINKOFF_INVEST_DOG_NEW
SDK_client = tinkoff.invest.Client(TOKEN)
User_acc_ID = intro.accid.ACC_ID
instrument_figi = 'FUTBR0922000'
open_positions_limit = 60000
close_time = datetime.time.fromisoformat('15:30:00')

count_time_base = datetime.datetime(1,1,1, close_time.hour, close_time.minute, close_time.second)
close_period_start = datetime.timedelta(minutes=1)
close_period_start = count_time_base + close_period_start
close_period_end = datetime.timedelta(minutes=30)
close_period_end = count_time_base + close_period_end



def future_structure(future: [tinkoff.invest.GetFuturesMarginResponse]):
    future_i = pd.DataFrame([{
        'initial_margin_on_buy': quotation_count(future.initial_margin_on_buy),
        'initial_margin_on_sell': quotation_count(future.initial_margin_on_sell),
        'min_price_increment': quotation_count(future.min_price_increment),
        'min_price_increment_amount': quotation_count(future.min_price_increment_amount)
    }])
    return future_i


def short_long(instrument: [tinkoff.invest.Future]):
    future_i_2 = pd.DataFrame([{
        'klong': quotation_count(instrument.klong),
        'kshort': quotation_count(instrument.kshort),
        'last_trade_day': pd.Timestamp(instrument.last_trade_date)
    }])
    return future_i_2


def future_info():
    with SDK_client as client:
        future_info_not_structured = client.instruments.get_futures_margin(figi=instrument_figi)
        short_long_coef = client.instruments.future_by(id_type=1, id=instrument_figi).instrument
        future_info_structured = future_structure(future_info_not_structured)
        appendix_1 = short_long(short_long_coef)
        fi = pd.concat([future_info_structured, appendix_1], axis=1)
        return fi


future_info_1 = future_info()
fi_a = future_info_1['min_price_increment'][0]
fi_b = future_info_1['min_price_increment_amount'][0]
fi_shortk = future_info_1['klong'][0]
fi_lolgk = future_info_1['kshort'][0]
fi_time = future_info_1['last_trade_day'][0]


def ma_ema_cross_strategy_test(historical_candles_df):
    hcdf = historical_candles_df
    open_positions = 0  # Счётчик открытых позиций
    check_rule = [bool, bool, bool]  # Массив для проверки по правилам
    condition_sell = [False, True, False]  # Правило 1
    condition_buy = [True, False, True]  # Правило 2
    ma = hcdf['ma']
    ema = hcdf['ema']
    time_line = hcdf['time']
    hcdf['contract_turnover'] = 0
    hcdf['deal'] = pd.NaT
    hcdf['commission'] = 0
    order_positions = 0
    hcdf.drop(columns=['Unnamed: 0'], inplace=True)
    # Проверка достаточности лимита/денег на счёте для открытия позиции
    if open_positions_limit < (hcdf.loc[0, 'close'] * fi_b / fi_a):
        print("Not enough money to open position or low limit")
        exit()
    else:
        print('Limit Success')

    for indx in range(len(hcdf)):
        indx_min_1 = indx - 1
        if indx_min_1 < 0:
            continue

        # Условия. В данном случае это проверка изменения соотношения MA и EMA средних с помощью 3-х соотношений.
        # 1 Проверка отношения значения EMA в текущем периоде к предыдущему
        if ema[indx] > ema[indx_min_1]:
            check_rule[0] = True
        else:
            check_rule[0] = False
        # 2 Проверка отношения значения MA в текущем периоде к EMA в текущем периоде
        if ma[indx] > ema[indx]:
            check_rule[1] = True
        else:
            check_rule[1] = False
        # 3 Проверка отношения значения MA в предыдущем периоде к EMA в предыдущем
        if ma[indx_min_1] > ema[indx_min_1]:
            check_rule[2] = True
        else:
            check_rule[2] = False

        # Расчёт открываемой позиции
        if open_positions == 0 and check_rule == condition_sell:
            order_positions = -1 * math.floor(open_positions_limit/(hcdf.loc[indx, 'close'] * fi_b/fi_a))
            # print('Order positions:', order_positions, 'condition_sell from 0')
        elif open_positions == 0 and check_rule == condition_buy:
            order_positions = math.floor(open_positions_limit/(hcdf.loc[indx, 'close'] * fi_b/fi_a))
            # print('Order positions:', order_positions, 'condition_buy from 0')
        elif indx == len(hcdf) - 2:
            order_positions = -1 * open_positions
            # print('Order positions:', order_positions, 'condition_close when close to the end of massive')
        elif open_positions < 0:
            order_positions = 2 * math.floor(open_positions_limit/(hcdf.loc[indx, 'close'] * fi_b/fi_a))
            # print('Order positions:', order_positions, 'condition_buy from open short positions')
        elif open_positions > 0:
            order_positions = -2 * math.floor(open_positions_limit/(hcdf.loc[indx, 'close'] * fi_b/fi_a))
            # print('Order positions:', order_positions, 'condition_buy from open short positions')
        # print(pd.Timestamp(time_line[indx]).day_of_week, time_line[indx], pd.Timestamp(time_line[indx]).ctime())
        hcdf.loc[indx, 'open_position'] = open_positions

        if close_period_end.time() >= pd.Timestamp(time_line[indx]).time() >= close_period_start.time():
            continue
        elif open_positions != 0 and \
            pd.Timestamp(time_line[indx]).day_of_week == 4 and \
            pd.Timestamp(time_line[indx]).time() >= close_time:
            hcdf.loc[indx, 'deal'] = 'week end'
            order_positions = open_positions
            hcdf.loc[indx, 'contract_turnover'] = -1 * order_positions * (hcdf.loc[indx, 'close'] / fi_a * fi_b)
            hcdf.loc[indx, 'commission'] = abs(order_positions * (hcdf.loc[indx, 'close'] / fi_a * fi_b) * 0.0004)
            hcdf.loc[indx, 'open_position'] = open_positions + -1 * order_positions
            hcdf.loc[indx, 'order_position'] = -1 * order_positions
            open_positions = open_positions + -1 * order_positions
            continue

        if check_rule == condition_buy and open_positions <= 0:
            hcdf.loc[indx, 'deal'] = 'buy'
            hcdf.loc[indx, 'contract_turnover'] = order_positions * (hcdf.loc[indx, 'close'] / fi_a * fi_b)
            hcdf.loc[indx, 'commission'] = abs(order_positions * (hcdf.loc[indx, 'close'] / fi_a * fi_b) * 0.0004)
            hcdf.loc[indx, 'open_position'] = open_positions + order_positions
            hcdf.loc[indx, 'order_position'] = order_positions
            open_positions = open_positions + order_positions
        elif check_rule == condition_sell and open_positions >= 0:
            hcdf.loc[indx, 'deal'] = 'sell'
            hcdf.loc[indx, 'contract_turnover'] = order_positions * (hcdf.loc[indx, 'close'] / fi_a * fi_b)
            hcdf.loc[indx, 'commission'] = abs(order_positions * (hcdf.loc[indx, 'close'] / fi_a * fi_b) * 0.0004)
            hcdf.loc[indx, 'open_position'] = open_positions + order_positions
            hcdf.loc[indx, 'order_position'] = order_positions
            open_positions = open_positions + order_positions
        elif indx == len(hcdf) - 10:
            print('last one done')
            hcdf.loc[indx, 'deal'] = 'close'
            hcdf.loc[indx, 'contract_turnover'] = -1 * order_positions / 2 * (hcdf.loc[indx, 'close'] / fi_a * fi_b)
            hcdf.loc[indx, 'commission'] = abs(-1 * order_positions / 2 * (hcdf.loc[indx, 'close'] / fi_a * fi_b) * 0.0004)
            hcdf.loc[indx, 'open_position'] = open_positions + order_positions / 2
            hcdf.loc[indx, 'order_position'] = -1 * order_positions / 2
            open_positions = open_positions + -1 * order_positions / 2
            print(open_positions)
            break
        else:
            hcdf.loc[indx, 'open_position'] = open_positions
            hcdf.loc[indx, 'order_position'] = order_positions
            open_positions = open_positions
            # print('no actions')

    # Далее три опции:
    # Построение графика при необходимости (нужно еще раскомментировать импорт matplotlib)
    # with plt.style.context('Solarize_Light2'):
    #     a = hcdf['time']
    #     b = hcdf['close']
    #     c = hcdf['ma']
    #     d = hcdf['ema']
    #     plt.plot(a, b, a, c, a, d)
    #     plt.show()
    # Вывод полученных значений
    # hcdf.drop(columns=['Unnamed: 0'], inplace=True)
    hcdf.dropna(how='any', inplace=True)
    print(hcdf)
    # Запись значений в файл со своим названием
    # hcdf.to_csv('csv_files/brent062022_orders.csv', mode='w')
    # print('Record to file complete')
    return hcdf


def check_profits(operations_df):
    operations_df.dropna(how='any', inplace=True)
    trade_result = 0
    commision_sum = 0
    # o = operations_df['contract_turnover']
    # c = operations_df['commission']
    for i in range(len(operations_df)):

        trade_result += operations_df['contract_turnover'].iloc[i]
        commision_sum += operations_df['commission'].iloc[i]

    return print('trade result = ', trade_result - commision_sum, '\n',
                 'only operations =', trade_result)


def record_orders_results(operations_df):
    operations_df.dropna(how='any', inplace=True)
    operations_df.to_csv('csv_files/brent092022_7-8mnth_report.csv', mode='w')
    return print('Record orders results complete')


test = ma_ema_cross_strategy_test(hist_candles_inst)
record_orders_results(test)
report = pd.read_csv('csv_files/brent092022_7-8mnth_report.csv')
check_profits(report)
