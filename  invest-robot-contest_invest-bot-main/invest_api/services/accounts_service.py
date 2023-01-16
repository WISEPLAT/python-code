import logging

from tinkoff.invest import Client, AccessLevel, AccountType, AccountStatus

from configuration.settings import AccountSettings
from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry

__all__ = ("AccountService")

logger = logging.getLogger(__name__)


class AccountService:
    """
    The class encapsulate tinkoff account api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    @invest_api_retry()
    @invest_error_logging
    def trading_account_id(self, account_settings: AccountSettings) -> str:
        """
        Method returns appropriate account id for trading:
        Full rights, common type (avoid IIS etc), account is open and ready,
        liquid_portfolio more that configured,
        green margin status (liquid > starting_margin)
        Account with high liquid_portfolio will be selected if more that one found
        """
        result = None
        max_liquid_portfolio = -1

        with Client(self.__token, app_name=self.__app_name) as client:
            logger.info("List of client accounts:")

            for account in client.users.get_accounts().accounts:
                logger.info(f"Account settings: {account}")

                if account.access_level == AccessLevel.ACCOUNT_ACCESS_LEVEL_FULL_ACCESS \
                        and account.type == AccountType.ACCOUNT_TYPE_TINKOFF \
                        and account.status == AccountStatus.ACCOUNT_STATUS_OPEN:

                    account_margin = client.users.get_margin_attributes(account_id=account.id)
                    logger.info(f"Account margin attributes: {account_margin}")

                    if account_margin.liquid_portfolio.units >= account_settings.min_liquid_portfolio \
                            and account_margin.liquid_portfolio.units > account_margin.starting_margin.units:
                        logger.info(f"Account is ready for trading")

                        if max_liquid_portfolio < account_margin.liquid_portfolio.units:
                            max_liquid_portfolio = account_margin.liquid_portfolio.units
                            result = account.id

        return result

    @invest_api_retry()
    @invest_error_logging
    def __verify(self) -> bool:
        """
        Verification method. Just connect and read some settings.
        """
        logger.info(f"Start client verification. App name: {self.__app_name}")

        with Client(self.__token, app_name=self.__app_name) as client:
            accounts = client.users.get_accounts()

            logger.info("List of client accounts:")
            for account in accounts.accounts:
                logger.info(account)

            tariff = client.users.get_user_tariff()

            logger.info("Current unary limits:")
            for unary_limit in tariff.unary_limits:
                logger.info(f"Request per minutes: {unary_limit.limit_per_minute}")
                logger.info("\t" + "\n\t".join(unary_limit.methods))

            logger.info("Current stream limits:")
            for stream_limit in tariff.stream_limits:
                logger.info(f"Connections {stream_limit.limit}:")
                logger.info("\t" + "\n\t".join(stream_limit.streams))

            logger.info("Client information:")
            logger.info(client.users.get_info())

        logger.info("Verification has been passed successfully.")

        return True

    def verify_token(self) -> bool:
        """
        Tinkoff API token verification
        :return: True - token is good, False - Try another one.
        """
        try:
            return self.__verify()
        except Exception as ex:
            logger.error(f"Verify error - {repr(ex)}")
            return False
