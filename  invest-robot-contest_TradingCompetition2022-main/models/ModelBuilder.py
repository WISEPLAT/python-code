from models.TradingModel import TradingModel
from models.ARIMAdeMarkLong import ARIMAdeMarkLong
from models.ARIMAdeMarkLongHFT import ARIMAdeMarkLongHFT
from decimal import Decimal
from logger.LoggerFactory import LoggerFactory
from logger.BusinessLogger import BusinessLogger


class ModelBuilder:
    _MODEL_MAP = dict(
        ARIMAdeMarkLong=ARIMAdeMarkLong,
        ARIMAdeMarkLongHFT=ARIMAdeMarkLongHFT
    )

    @classmethod
    def buildModel(cls, model_name, ticker, config):
        model: TradingModel = cls._MODEL_MAP[model_name](ticker, config)
        model.custom_init()
        # ToDo Don't send config into model. Parse all config and set value into object

        if not model:
            return None

        stock_drop_limit = config.get(section='TradingStrategy', option='stock_drop_limit')
        stock_limit = config.get(section='TradingStrategy', option='stock_limit')
        stock_lot_limit = config.get(section='TradingStrategy', option='stock_lot_limit')
        if stock_drop_limit:
            model.stock_drop_limit = Decimal(stock_drop_limit)
        if stock_limit:
            model.stock_limit = Decimal(stock_limit)
        if stock_lot_limit:
            model.stock_lot_limit = stock_lot_limit

        # Log data
        LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.MODEL_CREATED,
                                                               model_name, model)
        return model



