from tinkoff.invest import Client, OrderDirection, OrderType
from trading import trade_help
from config.personal_data import get_token, get_account, get_account_type
from trading.trade_help import quotation_to_float
import sqlite3 as sl
from datetime import datetime
from trading.get_securities import security_name_by_figi
from trading.trade_help import in_lot_figi

"""

    Тут представлены все функции, которые отвечает за размещение ордеров на покупку/продаужу бумаг

"""

'''
    Функция для покупки ценных бумаг по заданной цене за бумагу
    Если цена не задана (равна нулю), то бумаги покупаются по лучшей рыночной цене
'''


def buy_order(figi, price, quantity_lots, user_id, account_id="", account_type="", via="else"):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            if price > 0.0:
                order = client.sandbox.post_sandbox_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    price=trade_help.to_quotation(price),
                    quantity=quantity_lots,
                    account_id=account_id,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                order = client.sandbox.post_sandbox_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    account_id=account_id,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                )
        else:
            if price > 0.0:
                order = client.orders.post_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    price=trade_help.to_quotation(price),
                    quantity=quantity_lots,
                    account_id=account_id,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                order = client.orders.post_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    account_id=account_id,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                )
    write_operation(order=order, user_id=user_id, via=via, account_id=account_id, account_type=account_type)

    return order


'''
    Функция для продажи ценных бумаг по заданной цене за бумагу
    Если цена не задана (равна нулю), то бумаги продаются по лучшей рыночной цене
'''


def sell_sfb(figi, price, quantity_lots, user_id, account_id="", account_type="", via="else"):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            if price > 0.0:
                try:
                    order = client.sandbox.post_sandbox_order(
                        order_id=str(datetime.utcnow().timestamp()),
                        figi=figi,
                        quantity=quantity_lots,
                        price=trade_help.to_quotation(price),
                        account_id=account_id,
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        order_type=OrderType.ORDER_TYPE_LIMIT,
                    )
                except:
                    return False
            else:
                try:
                    order = client.sandbox.post_sandbox_order(
                        order_id=str(datetime.utcnow().timestamp()),
                        figi=figi,
                        quantity=quantity_lots,
                        account_id=account_id,
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        order_type=OrderType.ORDER_TYPE_MARKET,
                    )
                except:
                    return False
        else:
            if price > 0.0:
                try:
                    order = client.orders.post_order(
                        order_id=str(datetime.utcnow().timestamp()),
                        figi=figi,
                        quantity=quantity_lots,
                        price=trade_help.to_quotation(price),
                        account_id=account_id,
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        order_type=OrderType.ORDER_TYPE_LIMIT,
                    )
                except:
                    return False
            else:
                try:
                    order = client.orders.post_order(
                        order_id=str(datetime.utcnow().timestamp()),
                        figi=figi,
                        quantity=quantity_lots,
                        account_id=account_id,
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        order_type=OrderType.ORDER_TYPE_MARKET,
                    )
                except:
                    return False

    write_operation(order=order, user_id=user_id, via=via, account_id=account_id, account_type=account_type)

    return order


'''
    Функция для отмены ордера по его id
'''


async def cancel_order(order_id, user_id, account_id="", account_type=""):
    with Client(get_token(user_id)) as client:

        if account_id == "":
            account_id = get_account(user_id=user_id)

        if account_type == "":
            account_type = get_account_type(user_id=user_id)

        if account_type == "sandbox":
            state = client.sandbox.get_sandbox_order_state(
                order_id=order_id,
                account_id=account_id,
            )

            order = client.sandbox.cancel_sandbox_order(
                order_id=order_id,
                account_id=account_id,
            )
        else:
            state = client.orders.get_order_state(
                order_id=order_id,
                account_id=account_id,
            )

            order = client.orders.cancel_order(
                order_id=order_id,
                account_id=account_id,
            )

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    direction = cursor.execute('SELECT direction FROM operations WHERE order_id=?', (order_id,)).fetchone()[0]
    if direction is not None:
        quantity_lots = state.lots_executed
        price = quotation_to_float(state.executed_order_price)
        commission = quotation_to_float(state.executed_commission)
        direction += "/canceled"
        quantity_total = quantity_lots * in_lot_figi(state.figi, user_id=user_id)
        price_total = quantity_total * price

        new_operation = (quantity_lots, quantity_total, price_total, commission, direction, order_id)

        cursor.execute(
            'UPDATE OPERATIONS SET quantity_lots = ?, quantity_total = ?, price_total = ?, commission = ?, direction '
            '= ? WHERE order_id '
            '= ?;',
            new_operation)
        connection.commit()

    return order


def write_operation(order, user_id, account_id, account_type, via="else"):
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    order_id = order.order_id

    date_op = datetime.now().strftime("%d.%m.%Y")
    time_op = datetime.now().strftime("%H:%M:%S")

    if order.direction == 2:
        direction = "sell"
    elif order.direction == 1:
        direction = "buy"
    else:
        direction = "else"

    figi = order.figi
    ticker = order.figi  # Доделать потом
    name = security_name_by_figi(figi=figi, user_id=user_id)

    quantity_lots = order.lots_requested
    in_lot = in_lot_figi(figi=figi, user_id=user_id)
    quantity_total = quantity_lots * in_lot_figi(figi=figi, user_id=user_id)

    price_position = quotation_to_float(order.initial_order_price)
    commission = quotation_to_float(order.initial_commission)
    price_total = price_position * quantity_total - commission

    currency = order.initial_order_price.currency

    message = order.message

    operation = (
        user_id, account_id, account_type, order_id, date_op, time_op, direction, figi, ticker, name, quantity_lots,
        in_lot,
        quantity_total, price_position, price_total,
        commission, currency, message, via)
    cursor.execute("INSERT INTO OPERATIONS (user_id, account_id, account_type, order_id, date_op, time_op, direction, "
                   "figi, ticker, name, "
                   "quantity_lots, in_lot, quantity_total, price_position, price_total, commission,currency, message, "
                   "via) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?);",
                   operation)
    connection.commit()
