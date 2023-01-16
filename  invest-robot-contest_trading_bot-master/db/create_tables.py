import sqlite3 as sl


def create_tables():
    connection = sl.connect("db/BotDB.db")

    # Таблица содержит данные обо всех проведённых операциях
    connection.execute('CREATE TABLE IF NOT EXISTS operations ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                       'user_id TEXT,'
                       'account_id TEXT,'
                       'account_type TEXT,'
                       'account_access TEXT,'
                       'order_id TEXT,'
                       'date_op TEXT,'
                       'time_op TEXT,'
                       'direction TEXT,'
                       'figi TEXT,'
                       'ticker TEXT,'
                       'name TEXT,'
                       'quantity_lots INTEGER,'
                       'in_lot INTEGER,'
                       'quantity_total INTEGER,'
                       'price_position REAL,'
                       'price_total REAL,'
                       'commission REAL,'
                       'currency TEXT,'
                       'message TEXT,'
                       'via TEXT)')

    # Таблица содержит данные о конфигурации стратегии EMA + ADX + MACD
    connection.execute('CREATE TABLE IF NOT EXISTS str1_config ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                       'user_id TEXT,'
                       'account_id TEXT,'
                       'account_type TEXT,'
                       'account_access TEXT,'
                       'figi TEXT,'
                       'name TEXT,'
                       'trade_status TEXT,'
                       'notif_status TEXT,'
                       'buy_price REAL,'
                       'currency TEXT,'
                       'quantity_lots INTEGER,'
                       'period INTEGER,'
                       'macd_border REAL,'
                       'adx_border REAL,'
                       'take_profit REAL,'
                       'stop_loss REAL)')

    # Таблица содержит данные пользователя, которые используются в данный момент
    connection.execute('CREATE TABLE IF NOT EXISTS users ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                       'user_id INTEGER NOT NULL,'
                       'first_name TEXT,'
                       'last_name TEXT,'
                       'username TEXT,'
                       'token TEXT,'
                       'account_id TEXT,'
                       'account_type TEXT,'
                       'account_access TEXT,'
                       'bot_access_level TEXT)')

    connection_message = sl.connect("db/message.db")

    connection_message.execute('CREATE TABLE IF NOT EXISTS message_type ('
                               'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                               'message_type INTEGER NOT NULL,'
                               'message TEXT)')

    connection_message.execute('CREATE TABLE IF NOT EXISTS messages ('
                               'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                               'message_type INTEGER NOT NULL,'
                               'user_id INTEGER,'
                               'account_type TEXT,'
                               'date_message TEXT,'
                               'time_message TEXT,'
                               'function TEXT,'
                               'user_text TEXT)')
    return 0
