import logging
from pathlib import Path

from services.account_info import prepare_account_info
from services.instruments_info_cache import init_instruments_cache
from utils import logger
from utils.util import delete_file_if_exists


def reset_robot():
    delete_file_if_exists('data/test_history')
    delete_file_if_exists('data/trading_info')
    delete_file_if_exists('data/cache_instruments')


def init_robot():
    logger.init_logger()

    Path("data").mkdir(parents=True, exist_ok=True)
    prepare_account_info()
    init_instruments_cache()
