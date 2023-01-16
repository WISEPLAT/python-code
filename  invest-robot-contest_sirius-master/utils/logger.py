import sys

import logging

from utils.settings import settings


def init_logger():
    log_setting = settings()['OTHER']['log_level']
    log_level = logging.DEBUG
    if log_setting == 'debug':
        log_level = logging.DEBUG
    if log_setting == 'info':
        log_level = logging.INFO
    if log_setting == 'warn':
        log_level = logging.WARN
    if log_setting == 'error':
        log_level = logging.ERROR

    logger = logging.getLogger()
    logger.handlers.clear()

    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler('logs.log', encoding='utf8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


