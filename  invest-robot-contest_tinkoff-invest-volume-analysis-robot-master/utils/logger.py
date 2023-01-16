import logging
import os
from datetime import datetime


def init_logging():
    date = datetime.now().strftime("%Y-%m-%d")
    # todo упростить, проверить на unix-системах
    log_file_path = os.path.join(os.path.dirname(__file__) + "\\..\\logs", f"log-{date}.log")
    format = "%(asctime)s %(levelname)s --- (%(filename)s).%(funcName)s(%(lineno)d):\t %(message)s"
    logging.basicConfig(
        format=format,
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_file_path, encoding="utf-8"),
            logging.StreamHandler()
        ])
