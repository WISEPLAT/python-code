from dataclasses import dataclass
from typing import List

from tinkoff.invest import (
    HistoricCandle,
    MoneyValue,
    Order,
    OrderDirection,
    OrderState,
    OrderType,
    PositionsSecurities,
    Quotation,
)


@dataclass(frozen=True)
class TraderDecision:
    """Base type for the trader decision"""

    pass


class CreateOrder(TraderDecision):
    """Trader decision to create a new order with the given parameters"""

    order_type: OrderType
    order_direction: OrderDirection
    price: Quotation
    quantity: int


class CancelOrder(TraderDecision):
    """Trader decision to cancel the not fulfilled order with the given `order_id`"""

    order_id: str


@dataclass(frozen=True)
class MarketData:
    """Market data for an asset"""

    bids: List[Order]
    asks: List[Order]
    candles: List[HistoricCandle]


@dataclass(frozen=True)
class AccountBalance:
    """Balance on the current account"""

    money: List[MoneyValue]
    securities: List[PositionsSecurities]


@dataclass(frozen=True)
class MarketState:
    """Current state used by traders to make a decision"""

    account_balance: AccountBalance
    market_data: MarketData
    opened_orders: List[OrderState]
