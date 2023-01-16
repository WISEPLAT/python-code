import datetime
import logging

from tinkoff.invest import Client, Quotation, StopOrderDirection, StopOrderExpirationType, StopOrderType, StopOrder

from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry

__all__ = ("StopOrderService")

logger = logging.getLogger(__name__)


class StopOrderService:
    """
    The class encapsulate tinkoff stop order service api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    @invest_api_retry()
    @invest_error_logging
    def __post_stop_order(
            self,
            account_id: str,
            figi: str,
            count_lots: int,
            price: Quotation,
            stop_price: Quotation,
            direction: StopOrderDirection,
            expiration_type: StopOrderExpirationType,
            stop_order_type: StopOrderType,
            expire_date: datetime
    ) -> str:
        with Client(self.__token, app_name=self.__app_name) as client:
            logger.debug(f"Post stop order for: {account_id}")

            return client.stop_orders.post_stop_order(
                figi=figi,
                quantity=count_lots,
                price=price,
                stop_price=stop_price,
                direction=direction,
                account_id=account_id,
                expiration_type=expiration_type,
                stop_order_type=stop_order_type,
                expire_date=expire_date
            ).stop_order_id

    @invest_api_retry()
    @invest_error_logging
    def get_stop_orders(self, account_id: str) -> list[StopOrder]:
        with Client(self.__token, app_name=self.__app_name) as client:
            return client.stop_orders.get_stop_orders(account_id=account_id).stop_orders

    @invest_api_retry()
    @invest_error_logging
    def cancel_stop_order(self, account_id: str, stop_order_id: str) -> None:
        with Client(self.__token, app_name=self.__app_name) as client:
            client.stop_orders.cancel_stop_order(account_id=account_id, stop_order_id=stop_order_id)
