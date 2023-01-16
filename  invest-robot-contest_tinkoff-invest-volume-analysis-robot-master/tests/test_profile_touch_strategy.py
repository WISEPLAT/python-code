import csv
import datetime
import logging

import pandas as pd

from services.order_service import OrderService
from strategies.profile_touch_strategy import ProfileTouchStrategy
from utils.logger import init_logging
from utils.parse_util import parse_date
from utils.format_util import fixed_float
from utils.strategy_util import apply_frame_type

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.width = None

init_logging()
logger = logging.getLogger(__name__)


class TestProfileTouchStrategy:
    def __init__(self, instrument_name, file_path):
        self.instrument_name = instrument_name
        self.file_path = file_path

        self.df = pd.DataFrame(columns=["figi", "direction", "price", "quantity", "time"])
        self.df = apply_frame_type(self.df)

        self.profile_touch_strategy = ProfileTouchStrategy(instrument_name)
        self.profile_touch_strategy.start()

        self.order_service = OrderService()
        self.order_service.start()

    def run(self):
        test_start_time = datetime.datetime.now()
        logger.info("анализ истории: %s", self.file_path)

        with open(self.file_path, newline='') as file:
            reader = csv.DictReader(file, delimiter=",")
            for row in reader:
                figi = row["figi"]
                price = float(row["price"])
                time = parse_date(row["time"])

                processed_trade_df = pd.DataFrame.from_records([
                    {
                        "figi": figi,
                        "direction": row["direction"],
                        "price": price,
                        "quantity": row["quantity"],
                        "time": pd.to_datetime(str(time), utc=True),
                    }
                ])
                self.order_service.processed_orders(self.instrument_name, price, time)

                processed_trade_df = apply_frame_type(processed_trade_df)
                orders = self.profile_touch_strategy.analyze(processed_trade_df)
                if orders is not None:
                    for order in orders:
                        self.order_service.create_order(order)

        # после завершения анализа перестраиваю график, т.к. закрытие торгов не совпадает целому часу
        # например 15:59:59.230333+00:00
        self.profile_touch_strategy.calculate_clusters()
        self.order_service.write_statistics()

        test_end_time = datetime.datetime.now()
        total_test_time = (test_end_time - test_start_time).total_seconds() / 60
        logger.info("анализ завершен")
        logger.info("время тестирования: %s мин.", fixed_float(total_test_time))


if __name__ == "__main__":
    usd_histories = {"name": "USD000UTSTOM",
                     "files": ["./../data/USD000UTSTOM-20220504.csv", "./../data/USD000UTSTOM-20220505.csv",
                               "./../data/USD000UTSTOM-20220506.csv", "./../data/USD000UTSTOM-20220511.csv",
                               "./../data/USD000UTSTOM-20220512.csv", "./../data/USD000UTSTOM-20220513.csv",
                               "./../data/USD000UTSTOM-20220516.csv", "./../data/USD000UTSTOM-20220517.csv",
                               "./../data/USD000UTSTOM-20220518.csv", "./../data/USD000UTSTOM-20220519.csv",
                               "./../data/USD000UTSTOM-20220520.csv"]}

    sber_histories = {"name": "SBER",
                      "files": ["./../data/SBER-20220504.csv", "./../data/SBER-20220505.csv",
                                "./../data/SBER-20220506.csv", "./../data/SBER-20220511.csv",
                                "./../data/SBER-20220512.csv", "./../data/SBER-20220513.csv",
                                "./../data/SBER-20220516.csv", "./../data/SBER-20220517.csv",
                                "./../data/SBER-20220518.csv", "./../data/SBER-20220519.csv",
                                "./../data/SBER-20220520.csv"]}

    gaz_histories = {"name": "GAZP",
                     "files": ["./../data/GAZP-20220504.csv", "./../data/GAZP-20220505.csv",
                               "./../data/GAZP-20220506.csv", "./../data/GAZP-20220511.csv",
                               "./../data/GAZP-20220512.csv", "./../data/GAZP-20220513.csv",
                               "./../data/GAZP-20220516.csv", "./../data/GAZP-20220517.csv",
                               "./../data/GAZP-20220518.csv", "./../data/GAZP-20220519.csv",
                               "./../data/GAZP-20220520.csv", ]}

    for history in [usd_histories, sber_histories, gaz_histories]:
        for file_path in history["files"]:
            tester = TestProfileTouchStrategy(history["name"], file_path)
            tester.run()
