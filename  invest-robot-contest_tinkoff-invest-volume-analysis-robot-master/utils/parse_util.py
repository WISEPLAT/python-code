from datetime import datetime
from typing import Dict

import pandas as pd

from utils.format_util import quotation_to_float


def processed_data(trade):
    try:
        if trade is None:
            return

        price = quotation_to_float(trade.price)
        data = pd.DataFrame.from_records([
            {
                "figi": trade.figi,
                "direction": trade.direction,
                "price": price,
                "quantity": trade.quantity,
                "time": pd.to_datetime(str(trade.time), utc=True)
            }
        ])

        return data
    except Exception as ex:
        return ex


def parse_date(str_date: str):
    try:
        return datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S.%f%z")
    except ValueError:
        pass

    try:
        return datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S%z")
    except ValueError:
        pass

    return None


def get_float_from_dict(dictionary: Dict, key: str) -> float:
    if key in dictionary:
        return float(dictionary.get(key))
    return 0


def get_int_value(dictionary: Dict, key: str) -> int:
    if key in dictionary:
        return int(dictionary.get(key))
    return 0


def get_datetime_value(dictionary: Dict, key: str):
    if key in dictionary:
        return pd.to_datetime(dictionary.get(key))
    return None
