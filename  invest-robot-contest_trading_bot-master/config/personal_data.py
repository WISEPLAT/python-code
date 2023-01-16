import os
import sqlite3 as sl
from dotenv import load_dotenv
from config.crypto_rsa import decrypt

"""
    Все персональные данные хранятся в файле .env для обеспечения безопасности 
"""


def get_token(user_id):
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    token = cursor.execute('SELECT token FROM users WHERE user_id = ? ', (user_id,)).fetchone()[0]
    return decrypt(token)


def get_account(user_id):
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    account_id = cursor.execute('SELECT account_id FROM users WHERE user_id = ? ', (user_id,)).fetchone()[0]
    return account_id


def get_account_type(user_id):
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    account_type = cursor.execute('SELECT account_type FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
    return account_type


def get_account_access(user_id):
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    account_type = cursor.execute('SELECT account_access FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
    return account_type

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
