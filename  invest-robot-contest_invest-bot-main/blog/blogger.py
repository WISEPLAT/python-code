import asyncio
import logging
from decimal import Decimal

from tinkoff.invest import OrderState

from configuration.settings import BlogSettings, StrategySettings
from invest_api.utils import moneyvalue_to_decimal
from trade_system.signal import SignalType
from trade_system.strategies.base_strategy import IStrategy
from trading.trade_results import TradeOrder

__all__ = ("Blogger")

logger = logging.getLogger(__name__)


class Blogger:
    """
    Class formats and sends messages to telegram chat.
    """
    def __init__(
            self,
            blog_settings: BlogSettings,
            trade_strategies: list[StrategySettings],
            messages_queue: asyncio.Queue
    ) -> None:
        self.__blog_status = blog_settings.blog_status
        self.__trade_strategies: dict[str, StrategySettings] = {x.figi: x for x in trade_strategies}
        self.__messages_queue = messages_queue

    def __send_text_message(self, text: str) -> None:
        try:
            logger.debug(f"Put message to telegram messages queue: {text}")

            self.__messages_queue.put_nowait(text)
        except Exception as ex:
            logger.error(f"Error put message to telegram messages queue: {repr(ex)}")

    def start_trading_message(
            self,
            today_trade_strategy: dict[str, IStrategy],
            rub_before_trade_day: Decimal
    ) -> None:
        """
        The method sends message about depo size, list of stocks for today trading and greetings also.
        """
        if self.__blog_status:
            self.__send_text_message("Greetings! We are starting.")
            self.__send_text_message(f"Depo size: {rub_before_trade_day:.2f} rub")
            self.__send_text_message("Stocks list:")
            for figi_key, strategy_value in today_trade_strategy.items():
                self.__send_text_message(
                    f"Ticker: {strategy_value.settings.ticker}. "
                    f"Short trade status: {strategy_value.settings.short_enabled_flag}"
                )

    def finish_trading_message(self) -> None:
        """
        The method sends information that trading is stopping.
        """
        if self.__blog_status:
            self.__send_text_message("We are closing trading day.")

    def close_position_message(self, trade_order: TradeOrder) -> None:
        """
        The method sends information about closed position.
        """
        if self.__blog_status and trade_order:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            self.__send_text_message(
                f"{self.__trade_strategies[trade_order.signal.figi].ticker} position {signal_type} has been closed."
            )

    def open_position_message(self, trade_order: TradeOrder) -> None:
        """
        The method sends information about opened position.
        """
        if self.__blog_status and trade_order:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            self.__send_text_message(
                f"{self.__trade_strategies[trade_order.signal.figi].ticker} position {signal_type} has been opened. "
                f"Take profit level: {trade_order.signal.take_profit_level:.2f}. "
                f"Stop loss level: {trade_order.signal.stop_loss_level:.2f}."
            )

    def trading_depo_summary_message(
            self,
            rub_before_trade_day: Decimal,
            current_rub_on_depo: Decimal
    ) -> None:
        """
        The method sends information about trading day summary.
        """
        if self.__blog_status:
            self.__send_text_message(
                f"Start depo: {rub_before_trade_day:.2f} close depo:{current_rub_on_depo:.2f}."
            )

            today_profit = current_rub_on_depo - rub_before_trade_day
            today_percent_profit = (today_profit / rub_before_trade_day) * 100
            self.__send_text_message(f"Today leverage: {today_profit:.2f} rub ({today_percent_profit:.2f} %)")

    def fail_message(self):
        """
        The method sends information about emergency situation in bot.
        """
        if self.__blog_status:
            self.__send_text_message(
                f"Something went wrong. We are trying to close all positions. "
                f"If we fail, please try to do it himself."
            )

    def summary_message(self):
        """
        The method sends just summary title.
        """
        if self.__blog_status:
            self.__send_text_message(f"Trading day summary:")

    def final_message(self):
        """
        The method sends just goodbye title.
        """
        if self.__blog_status:
            self.__send_text_message(f"Trading has been completed. See you on next trade day!")

    def summary_open_signal_message(self, trade_order: TradeOrder, open_order_state: OrderState):
        """
        The method sends summary information about only open positions (not closed)
        """
        if self.__blog_status:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            summary_commission = moneyvalue_to_decimal(open_order_state.executed_commission) + \
                                 moneyvalue_to_decimal(open_order_state.service_commission)
            self.__send_text_message(
                f"Open {signal_type} position for {self.__trade_strategies[trade_order.signal.figi].ticker}. "
                f"Lots executed: {open_order_state.lots_executed}. "
                f"Average price: "
                f"{moneyvalue_to_decimal(open_order_state.average_position_price):.2f}. "
                f"Total order price: "
                f"{moneyvalue_to_decimal(open_order_state.total_order_amount):.2f}. "
                f"Total commissions: "
                f"{summary_commission:.2f}. "
                f"You have to close position manually."
            )

    def summary_closed_signal_message(self,
                                      trade_order: TradeOrder,
                                      open_order_state: OrderState,
                                      close_order_state: OrderState
                                      ) -> None:
        """
        The method sends summary information about closed positions
        """
        if self.__blog_status:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            summary_commission = moneyvalue_to_decimal(open_order_state.executed_commission) + \
                                 moneyvalue_to_decimal(open_order_state.service_commission) + \
                                 moneyvalue_to_decimal(close_order_state.executed_commission) + \
                                 moneyvalue_to_decimal(close_order_state.service_commission)
            self.__send_text_message(
                f"Close {signal_type} position for {self.__trade_strategies[trade_order.signal.figi].ticker}. "
                f"Lots executed: {close_order_state.lots_executed}. "
                f"Average open price: "
                f"{moneyvalue_to_decimal(open_order_state.average_position_price):.2f}. "
                f"Average close price: "
                f"{moneyvalue_to_decimal(close_order_state.average_position_price):.2f}. "
                f"Summary: "
                f"{moneyvalue_to_decimal(close_order_state.total_order_amount) - moneyvalue_to_decimal(open_order_state.total_order_amount):.2f}. "
                f"Total commissions: "
                f"{summary_commission:.2f}."
            )

    @staticmethod
    def __signal_type_to_message_test(signal_type: SignalType) -> str:
        return "long" if signal_type == SignalType.LONG else "short"
