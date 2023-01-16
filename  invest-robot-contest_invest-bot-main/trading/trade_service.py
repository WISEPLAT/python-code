import asyncio
import datetime
import logging

from blog.blogger import Blogger
from configuration.settings import AccountSettings, TradingSettings, BlogSettings, StrategySettings
from invest_api.services.accounts_service import AccountService
from invest_api.services.client_service import ClientService
from invest_api.services.instruments_service import InstrumentService
from invest_api.services.market_data_service import MarketDataService
from invest_api.services.operations_service import OperationService
from invest_api.services.orders_service import OrderService
from invest_api.services.market_data_stream_service import MarketDataStreamService
from trade_system.strategies.base_strategy import IStrategy
from trading.trader import Trader

__all__ = ("TradeService")

logger = logging.getLogger(__name__)


class TradeService:
    """
    Represent logic keep trading going
    """
    def __init__(
            self,
            account_service: AccountService,
            client_service: ClientService,
            instrument_service: InstrumentService,
            operation_service: OperationService,
            order_service: OrderService,
            stream_service: MarketDataStreamService,
            market_data_service: MarketDataService,
            blogger: Blogger,
            account_settings: AccountSettings,
            trading_settings: TradingSettings,
            strategies: list[IStrategy]
    ) -> None:
        self.__account_service = account_service
        self.__client_service = client_service
        self.__instrument_service = instrument_service
        self.__operation_service = operation_service
        self.__order_service = order_service
        self.__stream_service = stream_service
        self.__market_data_service = market_data_service
        self.__blogger = blogger
        self.__account_settings = account_settings
        self.__trading_settings = trading_settings
        self.__strategies = strategies

    async def worker(self) -> None:
        try:
            logger.info("Finding account for trading")
            account_id = self.__account_service.trading_account_id(self.__account_settings)

            if not account_id:
                logger.error("Account for trading hasn't been found")
                return None

            logger.info(f"Account id: {account_id}")

        except Exception as ex:
            logger.error(f"Start trading error: {repr(ex)}")
            return None

        await self.__working_loop(account_id)

    async def __working_loop(self, account_id: str) -> None:
        logger.info("Start every day trading")

        while True:
            logger.info("Check trading schedule on today")

            try:
                is_trading_day, start_time, end_time = \
                    self.__instrument_service.moex_today_trading_schedule()
                # for tests purposes
                #is_trading_day, start_time, end_time = \
                #    True, \
                #    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=10), \
                #    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=12)

                if is_trading_day and datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) <= end_time:
                    logger.info(f"Today is trading day. Trading will start after {start_time}")

                    await TradeService.__sleep_to(
                        start_time + datetime.timedelta(seconds=self.__trading_settings.delay_start_after_open)
                    )

                    logger.info(f"Trading day has been started")

                    await Trader(
                        client_service=self.__client_service,
                        instrument_service=self.__instrument_service,
                        operation_service=self.__operation_service,
                        order_service=self.__order_service,
                        stream_service=self.__stream_service,
                        market_data_service=self.__market_data_service,
                        blogger=self.__blogger
                    ).trade_day(
                        account_id,
                        self.__trading_settings,
                        self.__strategies,
                        end_time,
                        self.__account_settings.min_rub_on_account
                    )

                    logger.info("Trading day has been completed")
                else:
                    logger.info("Today is not trading day. Sleep on next morning")
            except Exception as ex:
                logger.error(f"Start trading today error: {repr(ex)}")

            logger.info("Sleep to next morning")
            await TradeService.__sleep_to_next_morning()

    @staticmethod
    async def __sleep_to_next_morning() -> None:
        future = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        next_time = datetime.datetime(year=future.year, month=future.month, day=future.day,
                                      hour=6, minute=0, tzinfo=datetime.timezone.utc)

        await TradeService.__sleep_to(next_time)

    @staticmethod
    async def __sleep_to(next_time: datetime) -> None:
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

        logger.debug(f"Sleep from {now} to {next_time}")
        total_seconds = (next_time - now).total_seconds()

        if total_seconds > 0:
            await asyncio.sleep(total_seconds)
