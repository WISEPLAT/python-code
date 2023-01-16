import datetime
import logging
from decimal import Decimal

from tinkoff.invest import Candle
from tinkoff.invest.utils import quotation_to_decimal

from blog.blogger import Blogger
from invest_api.services.client_service import ClientService
from invest_api.services.instruments_service import InstrumentService
from invest_api.services.market_data_service import MarketDataService
from invest_api.services.operations_service import OperationService
from invest_api.services.orders_service import OrderService
from invest_api.services.market_data_stream_service import MarketDataStreamService
from invest_api.utils import candle_to_historiccandle
from trade_system.signal import SignalType
from trade_system.strategies.base_strategy import IStrategy
from trading.trade_results import TradeResults
from configuration.settings import TradingSettings

__all__ = ("Trader")

logger = logging.getLogger(__name__)


class Trader:
    """
    The class encapsulate main trade logic.
    """

    def __init__(
            self,
            client_service: ClientService,
            instrument_service: InstrumentService,
            operation_service: OperationService,
            order_service: OrderService,
            stream_service: MarketDataStreamService,
            market_data_service: MarketDataService,
            blogger: Blogger
    ) -> None:
        self.__today_trade_results: TradeResults = None
        self.__client_service = client_service
        self.__instrument_service = instrument_service
        self.__operation_service = operation_service
        self.__order_service = order_service
        self.__stream_service = stream_service
        self.__market_data_service = market_data_service
        self.__blogger = blogger

    async def trade_day(
            self,
            account_id: str,
            trading_settings: TradingSettings,
            strategies: list[IStrategy],
            trade_day_end_time: datetime,
            min_rub: int
    ) -> None:
        logger.info("Start preparations for trading today")
        today_trade_strategies = self.__get_today_strategies(strategies)
        if not today_trade_strategies:
            logger.info("No shares to trade today.")
            return None

        self.__clear_all_positions(account_id, today_trade_strategies)

        rub_before_trade_day = self.__operation_service.available_rub_on_account(account_id)
        logger.info(f"Amount of RUB on account {rub_before_trade_day} and minimum for trading: {min_rub}")
        if rub_before_trade_day < min_rub:
            return None

        logger.info("Start trading today")
        self.__blogger.start_trading_message(today_trade_strategies, rub_before_trade_day)

        try:
            await self.__trading(
                account_id,
                trading_settings,
                today_trade_strategies,
                trade_day_end_time
            )
            logger.debug("Test Results:")
            logger.debug(f"Current: {self.__today_trade_results.get_current_open_orders()}")
            logger.debug(f"Old: {self.__today_trade_results.get_closed_orders()}")
        except Exception as ex:
            logger.error(f"Trading error: {repr(ex)}")

        logger.info("Finishing trading today")
        self.__blogger.finish_trading_message()

        try:
            if self.__today_trade_results:
                for key_figi, value_order_id in self.__clear_all_positions(account_id, today_trade_strategies).items():
                    trade_order = self.__today_trade_results.close_position(key_figi, value_order_id)
                    self.__blogger.close_position_message(trade_order)
            else:
                self.__clear_all_positions(account_id, today_trade_strategies)
        except Exception as ex:
            logger.error(f"Finishing trading error: {repr(ex)}")

        logger.info("Show trade results today")
        try:
            self.__summary_today_trade_results(account_id, rub_before_trade_day)
        except Exception as ex:
            logger.error(f"Summary trading day error: {repr(ex)}")

    async def __trading(
            self,
            account_id: str,
            trading_settings: TradingSettings,
            strategies: dict[str, IStrategy],
            trade_day_end_time: datetime
    ) -> None:
        logger.info(f"Subscribe and read Candles for {strategies.keys()}")

        # End trading before close trade session
        trade_before_time: datetime = \
            trade_day_end_time - datetime.timedelta(seconds=trading_settings.stop_trade_before_close)

        signals_before_time: datetime = \
            trade_day_end_time - datetime.timedelta(minutes=trading_settings.stop_signals_before_close)
        logger.debug(f"Stop time: signals - {signals_before_time}, trading - {trade_before_time}")

        current_candles: dict[str, Candle] = dict()
        self.__today_trade_results = TradeResults()

        async for candle in self.__stream_service.start_async_candles_stream(
                list(strategies.keys()),
                trade_before_time
        ):
            current_figi_candle = current_candles.setdefault(candle.figi, candle)
            if candle.time < current_figi_candle.time:
                # it can be based on API documentation
                logger.debug("Skip candle from past.")
                continue

            # check price from candle for take or stop price levels
            current_trade_order = self.__today_trade_results.get_current_trade_order(candle.figi)
            if current_trade_order:
                high, low = quotation_to_decimal(candle.high), quotation_to_decimal(candle.low)

                # Logic is:
                # if stop or take price level is between high and low, then stop or take will be executed
                if low <= current_trade_order.signal.stop_loss_level <= high:
                    logger.info(f"STOP LOSS: {current_trade_order}")
                    close_order_id = \
                        self.__close_position_by_figi(account_id, [candle.figi], strategies).get(candle.figi, None)
                    if close_order_id:
                        trade_order = self.__today_trade_results.close_position(candle.figi, close_order_id)
                        self.__blogger.close_position_message(trade_order)

                elif low <= current_trade_order.signal.take_profit_level <= high:
                    logger.info(f"TAKE PROFIT: {current_trade_order}")
                    close_order_id = \
                        self.__close_position_by_figi(account_id, [candle.figi], strategies).get(candle.figi, None)
                    if close_order_id:
                        trade_order = self.__today_trade_results.close_position(candle.figi, close_order_id)
                        self.__blogger.close_position_message(trade_order)

            if candle.time > current_figi_candle.time and \
                    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) <= signals_before_time:
                signal_new = strategies[candle.figi].analyze_candles(
                    [candle_to_historiccandle(current_figi_candle)]
                )

                if signal_new:
                    logger.info(f"New signal: {signal_new}")

                    if self.__today_trade_results.get_current_trade_order(candle.figi):
                        logger.info(f"New signal has been skipped. Previous signal is still alive.")
                    elif not self.__market_data_service.is_stock_ready_for_trading(candle.figi):
                        logger.info(f"New signal has been skipped. Stock isn't ready for trading")
                    else:
                        available_lots = self.__open_position_lots_count(
                            account_id,
                            strategies[candle.figi].settings.max_lots_per_order,
                            quotation_to_decimal(candle.close),
                            strategies[candle.figi].settings.lot_size
                        )

                        logger.debug(f"Available lots: {available_lots}")
                        if available_lots:
                            open_order_id = self.__order_service.post_market_order(
                                account_id=account_id,
                                figi=candle.figi,
                                count_lots=available_lots,
                                is_buy=(signal_new.signal_type == SignalType.LONG)
                            )
                            open_position = self.__today_trade_results.open_position(
                                candle.figi,
                                open_order_id,
                                signal_new
                            )
                            self.__blogger.open_position_message(open_position)
                            logger.info(f"Open position: {open_position}")
                        else:
                            logger.info(f"New signal has been skipped. No available money")

            current_candles[candle.figi] = candle

        logger.info("Today trading has been completed")

    def __summary_today_trade_results(
            self,
            account_id: str,
            rub_before_trade_day: Decimal
    ) -> None:
        logger.info("Today trading summary:")
        self.__blogger.summary_message()

        current_rub_on_depo = self.__operation_service.available_rub_on_account(account_id)
        logger.info(f"RUBs on account before:{rub_before_trade_day}, after:{current_rub_on_depo}")

        today_profit = current_rub_on_depo - rub_before_trade_day
        today_percent_profit = (today_profit / rub_before_trade_day) * 100
        logger.info(f"Today Profit:{today_profit} rub ({today_percent_profit} %)")
        self.__blogger.trading_depo_summary_message(rub_before_trade_day, current_rub_on_depo)

        if self.__today_trade_results:
            logger.info(f"Today Open Signals:")
            for figi_key, trade_order_value in self.__today_trade_results.get_current_open_orders().items():
                logger.info(f"Stock: {figi_key}")

                open_order_state = self.__order_service.get_order_state(account_id, trade_order_value.open_order_id)
                logger.info(f"Signal {trade_order_value.signal}")
                logger.info(f"Open: {open_order_state}")
                self.__blogger.summary_open_signal_message(trade_order_value, open_order_state)

            logger.info(f"All open positions should be closed manually.")

            logger.info(f"Today Closed Signals:")
            for figi_key, trade_orders_value in self.__today_trade_results.get_closed_orders().items():
                logger.info(f"Stock: {figi_key}")
                for trade_order in trade_orders_value:
                    open_order_state = self.__order_service.get_order_state(account_id, trade_order.open_order_id)
                    close_order_state = self.__order_service.get_order_state(account_id, trade_order.close_order_id)
                    logger.info(f"Signal {trade_order.signal}")
                    logger.info(f"Open: {open_order_state}")
                    logger.info(f"Close: {close_order_state}")
                    self.__blogger.summary_closed_signal_message(trade_order, open_order_state, close_order_state)
        else:
            logger.info(f"Something went wrong: today trade results is empty")
            logger.info(f"All open positions should be closed manually.")
            self.__blogger.fail_message()

        self.__blogger.final_message()

    def __open_position_lots_count(
            self,
            account_id: str,
            max_lots_per_order: int,
            price: Decimal,
            share_lot_size: int
    ) -> int:
        """
        Calculate counts of lots for order
        """
        current_rub_on_depo = self.__operation_service.available_rub_on_account(account_id)

        available_lots = int(current_rub_on_depo / (share_lot_size * price))

        return available_lots if max_lots_per_order > available_lots else max_lots_per_order

    def __clear_all_positions(
            self,
            account_id: str,
            strategies: dict[str, IStrategy]
    ) -> dict[str, str]:
        logger.info("Clear all orders and close all open positions")

        logger.debug("Cancel all order.")
        self.__client_service.cancel_all_orders(account_id)

        logger.debug("Close all positions.")
        return self.__close_position_by_figi(account_id, strategies.keys(), strategies)

    def __close_position_by_figi(
            self,
            account_id: str,
            figies: list[str],
            strategies: dict[str, IStrategy]
    ) -> dict[str, str]:
        result: dict[str, str] = dict()
        current_positions = self.__operation_service.positions_securities(account_id)

        if current_positions:
            logger.info(f"Current positions: {current_positions}")
            for position in current_positions:
                if position.figi in figies:
                    # Check a stock
                    if self.__market_data_service.is_stock_ready_for_trading(position.figi):
                        result[position.figi] = self.__order_service.post_market_order(
                            account_id=account_id,
                            figi=position.figi,
                            count_lots=abs(int(position.balance / strategies[position.figi].settings.lot_size)),
                            is_buy=(position.balance < 0)
                        )

        return result

    def __get_today_strategies(self, strategies: list[IStrategy]) -> dict[str, IStrategy]:
        """
        Check and Select stocks for trading today.
        """
        logger.info("Check shares and strategy settings")
        today_trade_strategy: dict[str, IStrategy] = dict()

        for strategy in strategies:
            share_settings = self.__instrument_service.share_by_figi(strategy.settings.figi)
            logger.debug(f"Check share settings for figi {strategy.settings.figi}: {share_settings}")

            if (not share_settings.otc_flag) \
                    and share_settings.buy_available_flag \
                    and share_settings.sell_available_flag \
                    and share_settings.api_trade_available_flag:
                logger.debug(f"Share is ready for trading")

                # refresh information by latest info
                strategy.update_lot_count(share_settings.lot)
                strategy.update_short_status(share_settings.short_enabled_flag)

                today_trade_strategy[strategy.settings.figi] = strategy

        return today_trade_strategy
