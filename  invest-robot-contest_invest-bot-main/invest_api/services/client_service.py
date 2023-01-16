import logging
from datetime import timedelta

from tinkoff.invest import CandleInterval, Client, HistoricCandle
from tinkoff.invest.utils import now

from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry

__all__ = ("ClientService")

logger = logging.getLogger(__name__)


class ClientService:
    """
    The class encapsulate tinkoff client api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    @invest_api_retry()
    @invest_error_logging
    def download_historic_candle(
            self,
            figi: str,
            from_days: int,
            interval: CandleInterval
    ) -> list[HistoricCandle]:
        """Download and return all requested historical candles"""
        result: list[HistoricCandle] = []

        from_ = now() - timedelta(days=from_days)
        logger.info(f"Start download recent candles. Figi: {figi}, from days: {from_}, interval: {interval.name}")

        with Client(self.__token, app_name=self.__app_name) as client:
            for candle in client.get_all_candles(
                    figi=figi,
                    from_=from_,
                    interval=interval
            ):
                logger.debug(candle)

                result.append(candle)

        logger.info(f"Download complete: candles count {len(result)}")

        return result

    @invest_api_retry()
    @invest_error_logging
    def cancel_all_orders(self, account_id: str) -> None:
        """ Cancel all open orders. """
        logger.info(f"Cancel all orders for account id: {account_id}")

        with Client(self.__token, app_name=self.__app_name) as client:
            client.cancel_all_orders(account_id=account_id)

        logger.info(f"Cancellation all orders complete.")
