from models.ARIMAdeMarkLong import ARIMAdeMarkLong
from models.ModelChecks import ModelChecks
from decimal import Decimal
from logger.BusinessLogger import BusinessLogger
from logger.LoggerFactory import LoggerFactory


class ARIMAdeMarkLongHFT(ARIMAdeMarkLong):
    # { Model checks name
    _PRICE_TAKE_PROFIT = "PRICE_TAKE_PROFIT"
    _PRICE_GR_PREV_PRICE = "PRICE_GR_PREV_PRICE"
    # Model checks name }

    def __init__(self, ticker, config):
        super(ARIMAdeMarkLongHFT, self).__init__(ticker, config)

        # DeMark Low and High level
        self._DeMark_low = None
        self._DeMark_high = None
        self._arima_predict_close = None

        # This model available only for LONG orders
        self._long_available = True
        self._short_available = False

        self._take_profit_percent = Decimal(self.get_config('take_profit_percent'))
        self._take_profit_value = None

    def _generate_check(self):
        """ Specifying all checks """

        check = self._check_handler
        # Adding check for OPEN LONG orders
        # Check 1 (OPEN LONG) Is price falls below LOW POINT of DeMark?
        check.add_check(ModelChecks.OPEN_LONG, self._LOW_POINT, self._is_price_low_point)
        check.add_check(ModelChecks.OPEN_LONG, self._PRICE_GR_PREV_PRICE, self.is_last_price_gr_prev_price)

        # Adding check for CLOSE LONG orders
        # Check 1 (CLOSE LONG) Is price up to take profit?
        check.add_check(ModelChecks.CLOSE_LONG, self._PRICE_TAKE_PROFIT, self._is_price_take_profit)

    def _is_price_take_profit(self):
        """ Check price is eq take profit or arima predict close"""
        if self._avg_price == 0:
            return False
        delta = self._avg_price * self._take_profit_percent / 100
        self._take_profit_value = self._avg_price + delta
        if self.last_price > self._take_profit_value or self.last_price > self._arima_predict_close:
            # Log data
            LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.TAKE_PROFIT,
                                                                   self._ticker, self.last_price)
            return True
        else:
            return False

    def is_last_price_gr_prev_price(self):
        """ Check is last price grader then prev price"""
        if self.last_price is None or self._prev_price is None:
            return False
        if self.last_price > self._prev_price:
            return True
        else:
            return False
