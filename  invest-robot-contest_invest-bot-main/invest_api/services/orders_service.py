import logging

from tinkoff.invest import Client, OrderDirection, Quotation, OrderType, PostOrderResponse, OrderState

from invest_api.utils import generate_order_id
from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry

__all__ = ("OrderService")

logger = logging.getLogger(__name__)


class OrderService:
    """
    The class encapsulate tinkoff order service api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    @invest_api_retry()
    @invest_error_logging
    def __post_order(
            self,
            account_id: str,
            figi: str,
            count_lots: int,
            price: Quotation,
            direction: OrderDirection,
            order_type: OrderType,
            order_id: str
    ) -> PostOrderResponse:
        with Client(self.__token, app_name=self.__app_name) as client:
            return client.orders.post_order(
                figi=figi,
                quantity=count_lots,
                price=price,
                direction=direction,
                account_id=account_id,
                order_type=order_type,
                order_id=order_id
            )

    def post_market_order(
            self,
            account_id: str,
            figi: str,
            count_lots: int,
            is_buy: bool
    ) -> str:
        """
        Post market order
        """
        logger.info(
            f"Post market order account_id: {account_id}, "
            f"figi: {figi}, count_lots: {count_lots}, is_buy: {is_buy}"
        )

        order_id = self.__post_order(
            account_id=account_id,
            figi=figi,
            count_lots=count_lots,
            price=None,
            direction=OrderDirection.ORDER_DIRECTION_BUY if is_buy else OrderDirection.ORDER_DIRECTION_SELL,
            order_type=OrderType.ORDER_TYPE_MARKET,
            order_id=generate_order_id()
        ).order_id

        logger.debug(f"order_id is {order_id}")

        return order_id

    @invest_api_retry()
    @invest_error_logging
    def cancel_order(self, account_id: str, order_id: str) -> None:
        with Client(self.__token, app_name=self.__app_name) as client:
            client.orders.cancel_order(account_id=account_id, order_id=order_id)

    @invest_api_retry()
    @invest_error_logging
    def get_order_state(self, account_id: str, order_id: str) -> OrderState:
        with Client(self.__token, app_name=self.__app_name) as client:
            return client.orders.get_order_state(account_id=account_id, order_id=order_id)

    @invest_api_retry()
    @invest_error_logging
    def get_orders(self, account_id: str) -> list[OrderState]:
        with Client(self.__token, app_name=self.__app_name) as client:
            return client.orders.get_orders(account_id=account_id).orders
