from logger.Logger import Logger, LogData
from datetime import datetime


class BusinessLogger(Logger):
    """
    Singleton Class for data logging
    Collect all event
    """
    ORDER_POSTED = "ORDER_POSTED"
    ORDER_OPEN_LONG_DONE = "ORDER_OPEN_LONG_DONE"
    ORDER_CLOSE_LONG_DONE = "ORDER_CLOSE_LONG_DONE"
    ACCOUNT_STARTED = "ACCOUNT_STARTED"
    ACCOUNT_BALANCE_NO_MONEY = "ACCOUNT_BALANCE_NO_MONEY"
    STOCK_IN_WORK = "STOCK_IN_WORK"
    STOCK_RE_INIT = "STOCK_RE_INIT"
    STOCK_DEL_FROM_SESS = "STOCK_DEL_FROM_SESSION"
    MODEL_CREATED = "MODEL_CREATED"
    CALC_STOP = "CALC_STOP"
    STOP_LOOS = "STOP_LOOS"
    TAKE_PROFIT = "TAKE_PROFIT"

    _LOGGER_INSTANCE: object = None
    log_line_dict = dict(datetime=datetime.now(), msg="")

    def __init__(self, conf_name_print_mode=None):
        if conf_name_print_mode is None:
            conf_name_print_mode = 'print_business_log'
        super().__init__(conf_name_print_mode)

    @classmethod
    def get_logger_instance(cls):
        if cls._LOGGER_INSTANCE is None:
            cls._LOGGER_INSTANCE = BusinessLogger()
        return cls._LOGGER_INSTANCE

    def add_event(self, event_type, obj, value=None):
        key = obj.id if hasattr(obj, 'id') else obj
        if value is None:
            value = obj
        log_data = LogData(event_id=event_type, key=key, value=value)
        self.add_log(log_data)

    def add_event_no_money(self, obj, balance, need_money):
        self.add_event(BusinessLogger.ACCOUNT_BALANCE_NO_MONEY,
                       obj, dict(balance=balance, need_money=need_money))
