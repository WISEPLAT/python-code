from logger.TechLogger import TechLogger
from logger.BusinessLogger import BusinessLogger
from datetime import datetime


class LoggerFactory:
    BUSINESS_LOGGER = 'BUSINESS_LOGGER'
    TECH_LOGGER = 'TECH_LOGGER'

    @classmethod
    def get_logger(cls, logger_type):
        logger = None
        file_name = None
        match logger_type:
            case cls.BUSINESS_LOGGER:
                logger = BusinessLogger().get_logger_instance()
                file_name = "Business_Log_" + str(datetime.now())
            case cls.TECH_LOGGER:
                logger = TechLogger().get_logger_instance()
                file_name = "Tech_Log_" + str(datetime.now())
        if logger and logger.file_name is None:
            logger.file_name = file_name
        return logger

    @classmethod
    def get_business_logger_instance(cls):
        return cls.get_logger(cls.BUSINESS_LOGGER)

    @classmethod
    def get_tech_logger_instance(cls):
        return cls.get_logger(cls.TECH_LOGGER)


def tech_log(fn):
    """ Decorator for log before and after fn """

    def logger(*args, **kwargs):
        log: TechLogger = LoggerFactory.get_tech_logger_instance()
        log.log_before_method(fn, *args, **kwargs)
        fn(*args, **kwargs)
        log.log_after_method(fn)
    return logger

