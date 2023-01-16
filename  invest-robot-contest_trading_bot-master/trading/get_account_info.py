from tinkoff.invest import Client, Quotation
from trading.trade_help import quotation_to_float
import pandas as pd
from config.personal_data import get_token, get_account_type, get_account
import sqlite3 as sl
import dataframe_image as dfi
from trading.trade_help import get_exchange_rate, get_currency_sing
from trading.get_securities import security_name_by_figi

'''

    Тут представлены все функции, которые позволяют получить какую-либо информацию о счёте
    
    Все данные будут храниться в pandas DataFrame для дальнейшей обработки
    
    Все значения, где количество или суммы представлены с помощью units (целая часть) и nano (дробная часть),
        сразу переводятся в дробные числа для удобства с помощью функции total_quantity.
    
'''

'''
    Функция для получения информации о свободной валюте на счёте
'''


def get_all_currency(user_id, account_id="", account_type=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            positions = client.sandbox.get_sandbox_positions(account_id=account_id)
        else:
            positions = client.operations.get_positions(account_id=account_id)

        currency_df = pd.DataFrame(
            {
                "currency": i.currency,
                "name": get_currency_name(user_id=user_id, currency=i.currency),
                "sign": get_currency_sing(currency=i.currency),
                "exchange_rate": get_exchange_rate(currency=i.currency),
                "sum": quotation_to_float(Quotation(units=i.units, nano=i.nano)),
                "sum_in_ruble": quotation_to_float(Quotation(units=i.units, nano=i.nano)) * get_exchange_rate(
                    currency=i.currency),
                "units": i.units,
                "nano": i.nano,
            } for i in positions.money
        )

    return currency_df


'''
    Функция для получения названия валюты
    Необходима для вывода информации по доступной валюте, так Тинькофф предоставляет только 
'''


def get_currency_name(user_id, currency):
    with Client(get_token(user_id)) as client:
        pos = client.instruments.currencies()

        for i in pos.instruments:
            if i.nominal.currency == currency:
                return i.name

    return ""


'''
    Функция для получения информации о всех купленных бумагах
'''


def get_all_securities(user_id, account_id="", account_type=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            portfolio = client.sandbox.get_sandbox_portfolio(account_id=account_id)
        else:
            portfolio = client.operations.get_portfolio(account_id=account_id)

        portfolio_df = pd.DataFrame(
            {
                "figi": i.figi,
                "instrument": i.instrument_type,
                "security_name": security_name_by_figi(figi=i.figi,user_id=user_id),
                "quantity": quotation_to_float(i.quantity),
                "average_price": quotation_to_float(i.average_position_price),
                "exp_yield": quotation_to_float(i.expected_yield),
                "nkd": quotation_to_float(i.current_nkd),
                "average_price_pt": quotation_to_float(i.average_position_price_pt),
                "current_price": quotation_to_float(i.current_price),
                "average_price_fifo": quotation_to_float(i.average_position_price_fifo),
                "lots": quotation_to_float(i.quantity_lots),
                "currency": i.average_position_price.currency,
                "currency_sign": get_currency_sing(i.average_position_price.currency)
            } for i in portfolio.positions
        )

    return portfolio_df


'''
    Функция для получения статистики по счёту
    Суммы по всем активам и предполагаемый доход/убыток
'''


def get_all_stat(user_id, account_id="", account_type=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            portfolio = client.sandbox.get_sandbox_portfolio(account_id=account_id)
        else:
            portfolio = client.operations.get_portfolio(account_id=account_id)

        stat_df = pd.DataFrame(
            {
                "sum_shares": quotation_to_float(portfolio.total_amount_shares),
                "sum_bonds": quotation_to_float(portfolio.total_amount_bonds),
                "sum_etf": quotation_to_float(portfolio.total_amount_etf),
                "sum_curr": quotation_to_float(portfolio.total_amount_currencies),
                "sum_fut": quotation_to_float(portfolio.total_amount_futures),
                "sum_total": quotation_to_float(portfolio.total_amount_shares) + quotation_to_float(
                    portfolio.total_amount_bonds) + quotation_to_float(portfolio.total_amount_etf) + quotation_to_float(
                    portfolio.total_amount_currencies) + quotation_to_float(portfolio.total_amount_futures),
                "exp_yield": quotation_to_float(portfolio.expected_yield),

            }, index=[0]
        )

    return stat_df


'''
    Функция для получения информации о количестве доступных лотов по figi
    
    Данная функция используется для проверки в боте, можно ли продать указанное количество акций
'''


def get_lots_portfolio(figi, user_id, account_id="", account_type=""):
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
                lots = int(quotation_to_float(i.quantity_lots))
                return int(lots)

    return 0


'''
    Функция для получения информации о цене бумаги в портфеле
'''


def get_price_in_portfolio(figi, user_id, account_id="", account_type=""):
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
                price = quotation_to_float(i.current_price)
                if price == 0.0:
                    price = quotation_to_float(i.average_position_price)
                return price

    return 0.0


'''
    Функция для получения списка открытых ордеров
'''


def get_my_order(user_id, account_id="", account_type=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            orders = client.sandbox.get_sandbox_orders(account_id=account_id).orders
        else:
            orders = client.orders.get_orders(account_id=account_id).orders

        order_df = pd.DataFrame(
            {
                "order_id": i.order_id,
                "lots_req": i.lots_requested,
                "lots_ex": i.lots_executed,
                "sum_req": quotation_to_float(i.initial_order_price),
                "sum_ex": quotation_to_float(i.executed_order_price),
                "sum_total": quotation_to_float(i.total_order_amount),  # сумма после всех комиссий
                "commission": quotation_to_float(i.initial_commission),
                "serv_commission": quotation_to_float(i.service_commission),
                "currency": i.currency,
                "currency_sign": get_currency_sing(i.currency),
                "figi": i.figi,
                "direction": i.direction,
                "price_one": quotation_to_float(i.initial_security_price),
                "order_date": i.order_date,
            } for i in orders
        )

    return order_df


'''
    Функция для получения списка всех операций пользователя
'''


def get_my_operations(user_id, account_id="", figi=""):
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    if account_id == "":
        account_id = get_account(user_id=user_id)

    if figi == "":
        operations = cursor.execute(
            'SELECT id, user_id, account_id, account_type, order_id, date_op, time_op, direction, figi, name, ticker, '
            'quantity_lots, in_lot, quantity_total, price_position, price_total, commission, currency, message, '
            'via FROM operations WHERE user_id = ? AND account_id = ?',
            (user_id, account_id)).fetchall()
    else:
        operations = cursor.execute(
            'SELECT id, user_id, account_id, account_type, order_id, date_op, time_op, direction, figi, name, ticker, '
            'quantity_lots, in_lot, quantity_total, price_position, price_total, commission, currency, message, '
            'via FROM operations WHERE user_id = ? AND account_id = ? AND figi = ?',
            (user_id, account_id, figi)).fetchall()

    if not operations:
        return False

    operations_df = pd.DataFrame(
        {
            "id": line[0],
            "user_id": user_id,
            "account_id": account_id,
            "account_type": line[3],
            "order_id": line[4],
            "date": line[5],
            "time": line[6],
            "direction": line[7],
            "figi": line[8],
            "name": line[9],
            "ticker": line[10],
            "quantity_lots": line[11],
            "in_lot": line[12],
            "quantity_total": line[13],
            "price_position": line[14],
            "price_total": line[15],
            "commission": line[16],
            "currency": line[17],
            "message": line[18],
            "via": line[19]
        } for line in operations
    )

    style_df = operations_df.drop(['id', 'user_id', 'order_id', 'figi', 'ticker'], axis=1)
    # style_df = style_df.style.apply(color_macd)

    dfi.export(style_df, f"img/operations/all_operations_{user_id}.png")

    return True
