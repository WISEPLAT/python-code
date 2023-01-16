from models.TradingModel import (TradingModel, ModelChecks)
from datetime import (date, timedelta, datetime)
import statsmodels.api as sm
import pandas as pd


class ARIMAdeMarkLong(TradingModel):
    """
    Trading Model ARIMA + DeMark
    ARIMA model forecasting trend and target
    DeMark - find point for open position (if the price falls below the point of low DeMark
                                           and come back to this point it will open position)
    """

    # { Model checks name
    _LOW_POINT = 'FALLS_BELOW_LOW_POINT'  # Price falls below low point of DeMark
    _IS_BACK_LOW_POINT = 'BACK_TO_LOW_POINT'  # Price come back to low point of DeMark
    _HIGH_POINT = 'UP_TO_HIGH_POINT'  # Price up to high point of DeMark
    # Model checks name }

    def __init__(self, ticker, config):
        super(ARIMAdeMarkLong, self).__init__(ticker, config)
        # DeMark Low and High level
        self._DeMark_low = None
        self._DeMark_high = None
        self._arima_predict_close = None

        # This model available only for LONG orders
        self._long_available = True
        self._short_available = False

    def custom_init(self):
        super(ARIMAdeMarkLong, self).custom_init()
        self._calculate_model()
        # Check calc of model is ok or not
        if self._check_model() is False:
            self._long_available = False

    def _check_model(self):
        """ Check model """
        if self._DeMark_low is None or self._DeMark_high is None:
            return False
        if self._DeMark_low > self._DeMark_high:
            return False
        if self._DeMark_low > self._arima_predict_close:
            return False
        return True

    def _calculate_model(self):
        """ Calculate ARIMA DeMark Model """
        prev_date = date.today() - timedelta(20)
        self._download_hist_data(start_date=prev_date, end_date=date.today())
        if len(self._hist_data) > 0:
            last_day = self._hist_data.iloc[-1]
            pivot = None
            if last_day.Close < last_day.Open:
                pivot = (last_day.High + (last_day.Low * 2) + last_day.Close)
            elif last_day.Close > last_day.Open:
                pivot = ((last_day.High * 2) + last_day.Low + last_day.Close)
            elif last_day.Close == last_day.Open:
                pivot = (last_day.High + last_day.Low + (last_day.Close * 2))
            if pivot:
                self._DeMark_high = pivot / 2 - last_day.Low
                self._DeMark_low = pivot / 2 - last_day.High
            self._arima_predict_close = self.__calc_arima()

    def __calc_arima(self):
        """ Calculate ARIMA """
        # Diff for Stationary
        fit_data = self._hist_data.Close.copy()
        fit_data = fit_data.diff(periods=1).dropna()

        all_date_index = pd.date_range(fit_data.index[0],
                                       fit_data.index[-1],
                                       freq="D")
        fit_data = fit_data.reindex(all_date_index)
        fit_data = fit_data.fillna(method='ffill')

        # Fit ARIMA
        arima_model = sm.tsa.ARIMA(fit_data, order=(1, 1, 1))
        arima_model_fited = arima_model.fit()

        # Predict for next day
        predict_date = datetime.today().date()
        arima_predict = arima_model_fited.predict(start=predict_date, end=predict_date, dynamic=False)

        # Convert Stationary back
        predict_date = str(predict_date.strftime('%Y-%m-%d'))
        prev_close = self._hist_data.Close[-1]
        arima_predict = arima_predict[predict_date] + prev_close

        return arima_predict

    def _generate_check(self):
        """ Specifying all checks """

        check = self._check_handler
        # Adding check for OPEN LONG orders
        # Check 1 (OPEN LONG) Is price falls below LOW POINT of DeMark?
        check.add_check(ModelChecks.OPEN_LONG, self._LOW_POINT, self._is_price_low_point)
        # Check 2 (OPEN LONG) Is price come back to LOW POINT of DeMark?
        check.add_check(ModelChecks.OPEN_LONG, self._IS_BACK_LOW_POINT, self._is_price_back_to_low_point)

        # Adding check for CLOSE LONG orders
        # Check 1 (CLOSE LONG) Is price up to below LOW POINT of DeMark?
        check.add_check(ModelChecks.CLOSE_LONG, self._HIGH_POINT, self._is_price_high_point)

    def _is_price_low_point(self):
        """ Check 1 (OPEN LONG) Is price falls below LOW POINT of DeMark? """
        if self._last_price < self._DeMark_low:
            return True
        return False

    def _is_price_back_to_low_point(self):
        """ Check 2 (OPEN LONG) Is price come back to LOW POINT of DeMark? """
        checks = self._check_handler.checks
        is_ready = checks[ModelChecks.OPEN_LONG][self._LOW_POINT][ModelChecks.IS_READY]
        if is_ready is True and self._last_price >= self._DeMark_low:
            return True
        return False

    def _is_price_high_point(self):
        """ Check 1 (CLOSE LONG) Is price up to below LOW POINT of DeMark or ARIMA close? """
        if self._last_price >= self._DeMark_high:
            return True
        if self._last_price >= self._arima_predict_close:
            return True
        return False
