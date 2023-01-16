from dataclasses import dataclass

from trade_system.signal import Signal

__all__ = ("TradeOrder")


@dataclass(frozen=False, eq=False, repr=True)
class TradeOrder:
    open_order_id: str
    signal: Signal
    close_order_id: str = ""


class TradeResults:
    """
    Keep history of orders by trade day
    """
    def __init__(self) -> None:
        self.__current_trade_orders: dict[str, TradeOrder] = dict()
        self.__old_trade_orders: dict[str, list[TradeOrder]] = dict()

    def get_current_open_orders(self) -> dict[str, TradeOrder]:
        return self.__current_trade_orders

    def get_closed_orders(self) -> dict[str, list[TradeOrder]]:
        return self.__old_trade_orders

    def get_current_trade_order(self, figi: str) -> TradeOrder:
        return self.__current_trade_orders.get(figi, None)

    def open_position(
            self,
            figi: str,
            open_order_id: str,
            signal: Signal
    ) -> TradeOrder:
        current_trade_order = self.get_current_trade_order(figi)

        if not current_trade_order:
            current_trade_order = TradeOrder(
                open_order_id=open_order_id,
                signal=signal
            )
            self.__current_trade_orders[figi] = current_trade_order

        return current_trade_order

    def close_position(
            self,
            figi: str,
            close_order_id: str
    ) -> TradeOrder:
        current_order = self.__current_trade_orders.pop(figi, None)

        if current_order:
            current_order.close_order_id = close_order_id
            (self.__old_trade_orders.setdefault(figi, [])).append(current_order)

        return current_order
