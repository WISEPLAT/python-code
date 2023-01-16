from models.TradingModel import TradingModel
from logger.LoggerFactory import tech_log


class Stock:
    """
    Class Stock provide full processing with ticker
    """

    def __init__(self, ticker):
        self._ticker = ticker  # ID of Stock
        self.id = self._ticker
        self._logger = None  # Object for collect log data
        self._model = None  # Link to trading model
        self._figi = None
        self._lot_available = 0
        self._count_in_lot = 0
        self.model_name = None
        self._config = None

    """
    { Setter/Getter
    """

    @property
    def ticker(self):
        return self._ticker

    @property
    def figi(self):
        return self._figi

    @figi.setter
    def figi(self, figi):
        self._figi = figi

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    @property
    def count_in_lot(self):
        return self._count_in_lot

    @count_in_lot.setter
    def count_in_lot(self, count):
        self._count_in_lot = count
        # ToDo Del this link. It is fast workaround :-(. (count_in_lot Should not be in both class
        self._model.count_in_lot = count

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model: TradingModel):
        self._model = model

    @property
    def lot_available(self):
        return self._lot_available

    @tech_log
    def set_available_lot(self, count):
        self._lot_available = count
        return self

    @property
    def is_trading_done(self) -> bool:
        model = self._model

        if model.is_long_available is True and model.is_long_open_done is True and model.is_long_close_done is True:
            return True
        # ToDo Add Short operation

        return False
