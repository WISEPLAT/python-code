from logger.Logger import Logger, LogData
from datetime import datetime


class TechLogger(Logger):
    """
    Singleton Class for tech logger
    Collect all tech event
    """

    _LOGGER_INSTANCE = None

    __BEFORE_METHOD = "BEFORE_METHOD"
    __AFTER_METHOD = "AFTER_METHOD"
    __METHOD_NAME = "METHOD_NAME"
    __INPUT_ARGS = 'INPUT_ARGS'
    __INPUT_KWARGS = 'INPUT_KWARGS'

    @classmethod
    def get_logger_instance(cls):
        if cls._LOGGER_INSTANCE is None:
            cls._LOGGER_INSTANCE = TechLogger()
        return cls._LOGGER_INSTANCE

    def __init__(self, conf_name_print_mode=None):
        if conf_name_print_mode is None:
            conf_name_print_mode = 'print_tech_log'
        super().__init__(conf_name_print_mode)

    def log_before_method(self, fn, *args, **kwargs):
        """ Before method started"""
        self.add_log(log_line_dict=LogData(event_id=self.__BEFORE_METHOD,
                                           datetime=datetime.today().now(),
                                           key=self.__METHOD_NAME, value=fn))
        for i in args:
            self.add_log(log_line_dict=LogData(event_id=self.__BEFORE_METHOD,
                                               datetime=datetime.today().now(),
                                               key=self.__INPUT_ARGS, value=str(i)))
        for i in kwargs:
            self.add_log(log_line_dict=LogData(event_id=self.__BEFORE_METHOD,
                                               datetime=datetime.today().now(),
                                               key=i, value=str(kwargs[i])))

    def log_after_method(self, fn):
        """ After method started"""
        self.add_log(log_line_dict=LogData(event_id=self.__AFTER_METHOD,
                                           datetime=datetime.today().now(),
                                           key=self.__METHOD_NAME, value=fn))

    def add_except(self, except_obj):
        log_data = LogData(event_id='EXCEPT', key=except_obj.code, value=except_obj, datetime=datetime.now())
        self.add_log(log_data)
