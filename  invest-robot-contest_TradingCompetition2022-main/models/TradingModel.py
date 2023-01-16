from decimal import Decimal
from models.ModelChecks import ModelChecks
import yfinance as yf
import pandas as pd
from logger.LoggerFactory import LoggerFactory
from logger.BusinessLogger import BusinessLogger


class TradingModel:
    """ Main class for developing trading model
    """

    def __init__(self, ticker, config):
        self._ticker = ticker
        self._config = config
        self._prev_price: Decimal = Decimal()  # ToDo Change to list of price (history)
        self._last_price: Decimal = Decimal()
        self._stop_price = None   # Calc stop loos price
        self._avg_price: Decimal = Decimal()    # Avg price of orders (buy)
        self._stock_limit: Decimal = Decimal()  # Limit for lot
        self._possible_lot: int = 0             # Possible lot for buy
        self._stock_drop_limit: int = 10        # Percent of drop limit
        self._count_in_lot = 0
        self._check_handler: ModelChecks = ModelChecks()

        # This model IS NOT available only for any type of orders
        self._long_available = False
        self._short_available = False

        self._long_open_ordered = False
        self._long_close_ordered = False

        self._long_open_done = False
        self._long_close_done = False

        self._hist_data: pd = None
        self._stock_lot_limit = None

    def custom_init(self):
        self._generate_check()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    def get_config(self, options):
        return self.config.get(section='TradingStrategy', option=options)

    def _check_model(self):
        return True

    def _calculate_model(self):
        """ Method for calculate model (should be implemented in each models ) """
        pass

    def _download_hist_data(self, start_date, end_date):
        """ Down load hist data for stock """
        # ToDo This data can be loaded few times (To avoid this, it should be stored in dict)
        ticker = self._ticker + '.ME'
        self._hist_data = yf.download(ticker, start=start_date, end=end_date, interval="1d")

    def _generate_check(self):
        """ Add all checks to self._check_handler (class ModelChecks) """
        pass

    def _run_checks(self):
        """ Run all checks for this model """
        for group, check_key, check in self._check_handler:
            if check[ModelChecks.IMPL_METHOD]() is True:
                self._check_handler.set_ready(group, check_key)

    def _is_all_true_in_group(self, group) -> bool:
        """ Is all check in group eq true? Group = OPEN_LONG, CLOSE_LONG, etc. """
        is_all_checks_true = False
        for check in self._check_handler.checks[group].values():
            is_all_checks_true = check[ModelChecks.IS_READY]
            if is_all_checks_true is False:
                break
        return is_all_checks_true

    @property
    def is_ready_to_open_long(self) -> bool:
        """ Check all specified checks, if all checks is true, it is time to open long order """
        if self._long_available is not True:
            return False

        # Is it already opened?
        if self.is_long_open_done is True:
            return False

        # Is it already ordered?
        if self._long_open_ordered is True:
            return False

        # Check possible lot to buy?
        if self.possible_lot == 0:
            return False



        return self._is_all_true_in_group(ModelChecks.OPEN_LONG)

    def calc_possible_lot(self):
        """
        Calc how many lot model can buy
        :return:
        """
        price_one_lot = self._last_price * self._count_in_lot
        if price_one_lot != 0:
            self._possible_lot = int(self._stock_limit // price_one_lot)

        if self._possible_lot == 0:
            self._possible_lot = self._stock_lot_limit
        else:
            self._possible_lot = min(self._possible_lot, self.stock_lot_limit)

    @property
    def stock_limit(self):
        return self._stock_limit

    @stock_limit.setter
    def stock_limit(self, limit):
        self._stock_limit = limit

    @property
    def count_in_lot(self):
        return self._count_in_lot

    @count_in_lot.setter
    def count_in_lot(self, count):
        self._count_in_lot = count

    @property
    def possible_lot(self):
        return self._possible_lot

    @property
    def stock_lot_limit(self) -> int:
        return int(self._stock_lot_limit)

    @stock_lot_limit.setter
    def stock_lot_limit(self, limit):
        self._stock_lot_limit = limit

    @property
    def is_ready_to_close_long(self) -> bool:
        """ Check all specified checks, if all checks is true, it is time to close long order """
        if self._long_available is not True:
            return False

        # Is it already close?
        if self.is_long_close_done is True:
            return False

        # Is it already ordered?
        if self._long_close_ordered is True:
            return False

        # Is open already done?
        if self._long_open_done is False:
            return False

        # Is it triggered STOP,
        if self.is_price_stop is True:
            return True

        return self._is_all_true_in_group(ModelChecks.CLOSE_LONG)

    @property
    def is_ready_to_open_short(self) -> bool:
        """ Check all specified checks, if all checks is true, it is time to open short order """
        if self._short_available is not True:
            return False
        return self._is_all_true_in_group(ModelChecks.OPEN_SHORT)

    @property
    def is_ready_to_close_short(self) -> bool:
        """ Check all specified checks, if all checks is true, it is time to close short order """
        if self._short_available is not True:
            return False
        return self._is_all_true_in_group(ModelChecks.CLOSE_SHORT)

    @property
    def is_long_open_done(self) -> bool:
        return self._long_open_done

    @is_long_open_done.setter
    def is_long_open_done(self, val: bool):
        self._long_open_done = val

    @property
    def is_long_close_done(self) -> bool:
        return self._long_close_done

    @is_long_close_done.setter
    def is_long_close_done(self, val: bool):
        self._long_close_done = val

    @property
    def is_long_open_ordered(self) -> bool:
        return self._long_open_ordered

    @property
    def is_long_close_ordered(self) -> bool:
        return self._long_close_ordered

    def long_open_ordered(self):
        self._long_open_ordered = True

    def long_close_ordered(self):
        self._long_close_ordered = True

    @property
    def last_price(self):
        return self._last_price

    def set_last_price(self, last_price):
        """Set last price into model"""
        self._prev_price = self._last_price
        self._last_price = Decimal(last_price)
        self.calc_possible_lot()
        self._run_checks()

    @property
    def is_long_available(self):
        return self._long_available

    @property
    def stock_drop_limit(self):
        return self._stock_drop_limit

    @stock_drop_limit.setter
    def stock_drop_limit(self, stock_drop_limit):
        self._stock_drop_limit = stock_drop_limit

    @property
    def is_price_stop(self) -> bool:
        """
        Check price for STOP
        :return:
        """
        if self._stop_price is None:
            # Stop price is no ready
            return False
        if self._last_price <= self._stop_price:
            # Log data
            LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.STOP_LOOS,
                                                                   self._ticker, self._last_price)
            return True

    def set_average_position_price(self, avg_price):
        self._avg_price = avg_price
        self.calc_stop_price()

    def calc_stop_price(self):
        if self._avg_price != 0:
            max_loos = self._avg_price * self._stock_drop_limit / 100
            self._stop_price = self._avg_price - max_loos
            # Log data
            LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.CALC_STOP,
                                                                   self._ticker, self._stop_price)
