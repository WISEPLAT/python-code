import datetime
import logging
from decimal import Decimal
from typing import Optional

from tinkoff.invest import Client, PositionsResponse, PositionsSecurities, OperationState, Operation, PortfolioResponse

from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry
from invest_api.utils import moneyvalue_to_decimal, rub_currency_name

__all__ = ("OperationService")

logger = logging.getLogger(__name__)


class OperationService:
    """
    The class encapsulate tinkoff operations service api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    def available_rub_on_account(self, account_id: str) -> Optional[Decimal]:
        """
        Return available amount of rub on account
        """
        position = self.__get_positions(account_id)

        if position:
            for money in position.money:
                if money.currency == rub_currency_name():
                    logger.debug(f"Amount of RUB on account: {money}")
                    return moneyvalue_to_decimal(money)

        return None

    def positions_securities(self, account_id: str) -> list[PositionsSecurities]:
        """
        :return: All open positions for account
        """
        positions = self.__get_positions(account_id)

        return positions.securities if positions else None

    @invest_api_retry()
    @invest_error_logging
    def __get_positions(self, account_id: str) -> PositionsResponse:
        with Client(self.__token, app_name=self.__app_name) as client:
            logger.debug(f"Get Positions for: {account_id}:")

            positions = client.operations.get_positions(account_id=account_id)

            logger.debug(f"{positions}")

            return positions

    @invest_api_retry()
    @invest_error_logging
    def __get_operations(
            self,
            account_id: str,
            from_: datetime,
            to_: datetime,
            state: OperationState,
            figi: str = ""
    ) -> list[Operation]:
        with Client(self.__token, app_name=self.__app_name) as client:
            logger.debug(f"Get operations for: {account_id}, from: {from_}, to: {to_}, state: {state}, figi: {figi}")

            operations = client.operations.get_operations(
                account_id=account_id,
                from_=from_,
                to=to_,
                state=state,
                figi=figi
            ).operations

            logger.debug(f"{operations}")

            return operations

    @invest_api_retry()
    @invest_error_logging
    def __get_portfolio(self, account_id: str) -> PortfolioResponse:
        with Client(self.__token, app_name=self.__app_name) as client:
            logger.debug(f"Get portfolio for: {account_id}")

            portfolio = client.operations.get_portfolio(account_id=account_id)

            logger.debug(f"{portfolio}")

            return portfolio
