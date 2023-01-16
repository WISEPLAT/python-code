"""This is the internal module for working with the database.
"""

import sqlite3
import os

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

_DB_NAME = os.getenv("TINVEST_DB_NAME") or '../data/tinvest-perevalov.sqlite'

def init_db():
    """Initializes database if not exists.
    """
    try:
        conn = sqlite3.connect(_DB_NAME) 
        c = conn.cursor()
        # Create table for news
        c.execute('''
                CREATE TABLE IF NOT EXISTS news
                ([news_id] INTEGER PRIMARY KEY AUTOINCREMENT, [news_text] TEXT, [news_sentiment] TEXT, [is_checked] BOOLEAN NOT NULL)
                ''')
        # Create table for orders
        c.execute('''
                CREATE TABLE IF NOT EXISTS orders
                ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [figi] TEXT, [quantity] INTEGER, [price] REAL, [direction] INTEGER, [account_id] TEXT, [order_type] INTEGER, [order_id] TEXT, [order_date] DATETIME, [news_id] INTEGER)
                ''')
    except Exception as e:
        logger.error(str(e))
    finally:
        c.close()
        conn.commit()
        conn.close()


def check_if_exists(news_text: str) -> bool:
    """Checks if news with given text already exists in database.
    Args:
        news_text (str): Headline of the news

    Returns:
        bool: Flag if news with given text already exists in database.
    """
    try:
        conn = sqlite3.connect(_DB_NAME) 
        c = conn.cursor()
                        
        c.execute(f'''
                SELECT news_id
                FROM news
                WHERE news_text LIKE "{news_text}"
                ''')

        data = c.fetchall()

        if len(data) > 0:
            return True
    except Exception as e:
        logger.error(str(e))
    finally:
        c.close()
        conn.commit()
        conn.close()

    return False


def put_in_db(news_text: str, sentiment: str):
    try:
        conn = sqlite3.connect(_DB_NAME) 
        c = conn.cursor()
                        
        c.execute(f'''
                INSERT INTO news (news_text, news_sentiment, is_checked)
                VALUES ("{news_text}", "{sentiment}", 0)
        ''')
    except Exception as e:
        logger.error(str(e))
    finally:
        c.close()
        conn.commit()
        conn.close()

def put_order_in_db(figi: str, quantity: int, price: float, direction: int, account_id: str, order_type: int, order_id: str, news_id: int):
    try:
        conn = sqlite3.connect(_DB_NAME) 
        c = conn.cursor()

        c.execute(f'''
            INSERT INTO orders (figi, quantity, price, direction, account_id, order_type, order_id, order_date, news_id)
            VALUES ("{figi}", {quantity}, {price}, {direction}, "{account_id}", {order_type}, "{order_id}", datetime('now'), {news_id})
        ''')
    except Exception as e:
        logger.error(str(e))
    finally:
        c.close()
        conn.commit()
        conn.close()

def update_is_checked(news_id: int):
    """Updates is_checked flag to 1 for news with given id.

    Args:
        news_id (int): News id to update.
    """
    try:
        conn = sqlite3.connect(_DB_NAME) 
        c = conn.cursor()
                        
        c.execute(f'''
            UPDATE news
            SET is_checked = 1
            WHERE news_id = {news_id}
        ''')
    except Exception as e:
        logger.error(str(e))
    finally:
        c.close()
        conn.commit()
        conn.close()

def select_not_checked() -> list:
    """Selects news that are not checked yet.

    Returns:
        list: a list of news that are not checked yet.
    """
    try:
        conn = sqlite3.connect(_DB_NAME) 
        c = conn.cursor()
                        
        c.execute(f'''
            SELECT news_id, news_text, news_sentiment
            FROM news
            WHERE is_checked = 0
        ''')

        data = [{'news_id': d[0], 'title': d[1], 'sentiment': d[2]} for d in c.fetchall()]

        return data
    except Exception as e:
        logger.error(str(e))
    finally:
        c.close()
        conn.commit()
        conn.close()

    return []