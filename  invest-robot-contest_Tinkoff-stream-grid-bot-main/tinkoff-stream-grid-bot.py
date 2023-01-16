import sqlite3
import time
import sys
import json
import logging
from tinkoff.invest import Client, RequestError
from tinkoff.invest import OrderType, OrderDirection, Quotation, OrderExecutionReportStatus

#for token import
import os

#Token import to variables
config_file = "config.json"

if os.path.isfile(config_file):
    with open(file=config_file) as config:
        config = json.load(config)
        TOKEN = config.get('token')
        ACCID = config.get('account_id')
        shares = config.get('shares')
else:
    print ("No " + config_file + " exists.")
    exit(0)

sqlite = sqlite3.connect('sqlite_brand_new_stream2.db')
cursor = sqlite.cursor()

logger = open('bot_stat.log', 'a')


def log(*args):
    message = ' '.join(map(str, args))
    print(message)
    logger.write(message + "\n")
    logger.flush()

def makefloat(m) -> float:
    return float(format(m.units + m.nano / 10 ** 9, '.9f'))

def makequotation(m) -> Quotation:
    return Quotation(*[int(a) for a in format(m, '.9f').split('.')])

def main() -> int:
    sql = '''CREATE TABLE IF NOT EXISTS `share` (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker VARCHAR(50) NOT NULL UNIQUE,
                figi VARCHAR(50)
            );'''
    cursor.execute(sql)
    sqlite.commit()

    sql = '''CREATE TABLE IF NOT EXISTS `price` (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_id INTEGER NOT NULL,
            ticker VARCHAR(50) NOT NULL,
            price DECIMAL(20,10) NOT NULL
        );'''
    cursor.execute(sql)
    sqlite.commit()

    sql = '''CREATE TABLE IF NOT EXISTS `order` (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_id INTEGER NOT NULL,
            ticker VARCHAR(50) NOT NULL,
            order_id VARCHAR(64) UNIQUE,
            price DECIMAL(20,10) NOT NULL,
            direction INTEGER
        );
    '''
    cursor.execute(sql)
    sqlite.commit()

    with Client(token=TOKEN, app_name="nazmiev.Tinkoff-stream-grid-bot") as client:
        for instrument in client.instruments.shares().instruments:
            if (instrument.ticker in shares):
                share = shares[instrument.ticker]
                share['ticker'] = instrument.ticker
                share['figi'] = instrument.figi
                share['min_price_step'] = makefloat(instrument.min_price_increment)

                cursor.execute("INSERT OR IGNORE INTO `share` (ticker, figi) VALUES (?, ?)", (instrument.ticker, instrument.figi))
                sqlite.commit()

                share['id'] = cursor.lastrowid if cursor.lastrowid else cursor.execute("SELECT id FROM `share` WHERE ticker = ?", (instrument.ticker, )).fetchone()[0]

        for ticker, share in shares.items():
            last_price = client.market_data.get_last_prices(figi=[share['figi']]).last_prices[0].price
            last_price = makefloat(last_price)
            print(ticker, share['figi'], "last price", last_price, "min step", share['min_price_step'])

            if share['start_price'] == 0:
                share['start_price'] = last_price

            # достать всё из базы. Если нет, то заполнить
            prices = get_prices(share)
            if prices:
                continue

            # удаляем все открытые ордера
            client.cancel_all_orders(account_id=ACCID)

            # заполняем цены
            for i in range(share['number'] + 1):
                price = share['start_price'] + share['start_price'] * share['price_step'] * (i - share['number'] / 2)
                price = round(price / share['min_price_step']) * share['min_price_step']
                price = float(format(price, '.9f'))

                cursor.execute("INSERT INTO `price` (share_id, ticker, price) VALUES (?, ?, ?)", (share['id'], ticker, price))
                sqlite.commit()


        # по ценам выставляем ордера
        for share in shares.values():
            create_orders(client, share)

        # засечь время
        orders_time = time.time()

        while True:
            try:
                for response in client.orders_stream.trades_stream([ACCID]):
                    print(time.asctime(), response)

                    if not response.order_trades:
                        print(time.asctime(), "not response.order_trades")
                        # если в базе нет ордеров и прошла минута пытаться перевыставить ордера
                        if time.time() - orders_time >= 1 * 60:
                            for share in shares.values():
                                create_orders(client, share)
                            orders_time = time.time()
                        continue

                    order_id = response.order_trades.order_id
                    handle_order(client, order_id)
                    orders_time = time.time()
            except RequestError as err:
                # неведомая ошибка
                print(time.asctime(), "неведомая ошибка", err)

    return 0

def create_orders(client, share):
    share_id = share['id']
    figi = share['figi']
    quantity = share['quantity']

    prices = get_prices(share)

    last_price = client.market_data.get_last_prices(figi=[figi]).last_prices[0].price
    last_price = makefloat(last_price)
    skip_price = 0
    for price in prices:
        if abs(price - last_price) < abs(price - skip_price):
            skip_price = price

    #пробуем найти цену под sell
    new_skip_price = cursor.execute(
        "SELECT MAX(price) FROM price P WHERE share_id = ? AND price < (SELECT MIN(price) FROM `order` WHERE direction = ? AND share_id = P.share_id)",
        (share_id, OrderDirection.ORDER_DIRECTION_SELL)).fetchone()[0]
    print(time.asctime(), 'new_skip_price sell', new_skip_price)

    if not new_skip_price:
        # пробуем найти цену над buy
        new_skip_price = cursor.execute(
            "SELECT MIN(price) FROM price P WHERE share_id = ? AND price > (SELECT MAX(price) FROM `order` WHERE direction = ? AND share_id = P.share_id)",
            (share_id, OrderDirection.ORDER_DIRECTION_BUY)).fetchone()[0]
        print(time.asctime(), 'new_skip_price buy', new_skip_price)

    if new_skip_price:
        print(time.asctime(), 'new_skip_price', new_skip_price)
        skip_price = new_skip_price

    print(time.asctime(), 'last', last_price, 'skip', skip_price)

    # пробуем выставлять ордера от текущей цены вверх и вниз, чтобы сначала пытался выставить ближайшие ордера, которые скорей всего сработают
    # sorted(prices, key=lambda x: abs(x - skip_price))

    for price in prices:
        # достать ордер из базы
        order = cursor.execute("SELECT order_id FROM `order` WHERE `share_id` = ? AND `price` = ?", (share_id, price)).fetchone()
        if order:
            handle_order(client, order[0])
            continue

        if price == skip_price:
            continue

        # create order
        direction = OrderDirection.ORDER_DIRECTION_SELL if price > last_price else OrderDirection.ORDER_DIRECTION_BUY
        price_quotation = makequotation(price)
        try:
            order = client.orders.post_order(account_id=ACCID, figi=figi, quantity=quantity,
                                             price=price_quotation, direction=direction,
                                             order_type=OrderType.ORDER_TYPE_LIMIT,
                                             order_id=str(time.time_ns()))
            # print('post_order', ACCID, figi, quantity, price_quotation, direction)
            # order = type('obj', (object,), { 'order_id': str(time.time_ns()) })

            cursor.execute("INSERT INTO `order` (share_id, ticker, order_id, price, direction) VALUES (?, ?, ?, ?, ?)",
                           [share_id, share['ticker'], order.order_id, price, direction])
            sqlite.commit()
            print(time.asctime(), "Выставил ордер: ", share['ticker'], price, direction)
        except RequestError as err:
            # попробовать поймать ошибку что нет торгов сейчас, например 30079. Все ошибки тут: https://tinkoff.github.io/investAPI/errors/
            print(time.asctime(), "Ошибка при выставлении ордера: ", share['ticker'], price, direction, err.metadata.message)
            if err.details == '30079':
                return

def handle_order(client, order_id):
    order = cursor.execute("SELECT id, share_id, price FROM `order` WHERE `order_id` = ?", (order_id, )).fetchone()
    if not order:
        print(time.asctime(), "not order: ", order)
        return
    id = order[0]
    share_id = order[1]
    price = order[2]

    share = None
    for tmp in shares.values():
        if tmp['id'] == share_id:
            share = tmp
            break
    if not share:
        print("share not found")
        return
    figi = share['figi']
    quantity = share['quantity']

    order_state = client.orders.get_order_state(account_id=ACCID, order_id=order_id)
    if not order_state:
        print(time.asctime(), "not order_state: ", order)
        return
    print(time.asctime(), order_state.execution_report_status)

    bad_statuses = [
        OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_UNSPECIFIED,
        OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED,
        OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED
    ]

    if (order_state.execution_report_status in bad_statuses):
        print(time.asctime(), " ORDER ", order_state.execution_report_status, order_id, price)
        cursor.execute("DELETE FROM `order` WHERE id = ?", (id,))
        sqlite.commit()
        return

    if (order_state.execution_report_status == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL):
        print(time.asctime(), " ORDER FILLED ", order_id, price)
        log(time.asctime(), " ORDER FILLED ", order_id, price, order_state.direction)

        prices = get_prices(share)

        direction = order_state.direction
        price_index = prices.index(price)

        if (direction == OrderDirection.ORDER_DIRECTION_SELL):
            direction = OrderDirection.ORDER_DIRECTION_BUY
            price_index -= 1
        else:
            direction = OrderDirection.ORDER_DIRECTION_SELL
            price_index += 1

        price = prices[price_index]
        price_quotation = makequotation(price)

        try:
            order = client.orders.post_order(account_id=ACCID, figi=figi, quantity=quantity,
                                             price=price_quotation, direction=direction,
                                             order_type=OrderType.ORDER_TYPE_LIMIT,
                                             order_id=str(time.time_ns()))
            # print('post_order', ACCID, figi, quantity, price_quotation, direction)
            # order = type('obj', (object,), {'order_id': str(time.time_ns())})

            cursor.execute("UPDATE `order` SET order_id = ?, price = ?, direction = ? WHERE id = ?",
                           [order.order_id, price, direction, id])
            sqlite.commit()
            print(time.asctime(), " NEW ORDER ", order.order_id, direction, price)
        except RequestError as err:
            print(time.asctime(), " ERROR ", err.metadata.message)

def get_prices(share):
    cursor.execute("SELECT price FROM `price` WHERE share_id = ? ORDER BY price", (share['id'], ))
    return [row[0] for row in cursor.fetchall()]

if __name__ == "__main__":
    sys.exit(main())