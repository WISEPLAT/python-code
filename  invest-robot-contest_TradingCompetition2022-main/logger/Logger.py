from os.path import exists
import csv
from datetime import datetime
from dataclasses import dataclass
import configparser


@dataclass(eq=False, repr=True)
class LogData:
    event_id: str
    key: str
    value: str
    datetime: datetime = datetime.now()


class Logger:
    """ Class for logger """
    """ ToDo Change log from CSV into DB"""

    log_line_dict = dict(datetime=datetime.now(), msg="")

    def __init__(self, conf_name_print_mode):
        self._file_name = None
        self._log_storage = list()
        self._header = ["event_id", "datetime", "key", "value"]
        self._print_mode = None
        self._config = configparser.ConfigParser()
        self._config.read('config.ini')
        self._print_mode = True if self._config.get(section='main', option=conf_name_print_mode) == 'True' else False

    @property
    def print_mode(self):
        return self._print_mode

    @print_mode.setter
    def print_mode(self, mode):
        self._print_mode = mode

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        self._file_name = "logger/log_result/" + file_name + '.csv'
        if not exists(self._file_name):
            self.create_csv_file()

    def create_csv_file(self):

        with open(self._file_name, 'w', encoding='UTF8', newline='') as file:
            # writer = csv.DictWriter(file,delimiter=";")
            writer = csv.DictWriter(file, fieldnames=self._header)
            writer.writeheader()

    def save_log(self, log_line_dict: LogData):
        # Convert data
        with open(self._file_name, 'a', encoding='UTF8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self._header)
            writer.writerow({'event_id': log_line_dict.event_id, 'key': log_line_dict.key,
                             'value': log_line_dict.value, 'datetime': log_line_dict.datetime})

    def add_log(self, log_line_dict: LogData):
        log_line_dict.datetime = datetime.today().now()
        if self._print_mode:
            # ToDo
            self._print_start()
            print(log_line_dict)
            self._print_end()
        self._log_storage.append(log_line_dict)
        self.save_log(log_line_dict)

    @staticmethod
    def _print_start():
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    @staticmethod
    def _print_end():
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
