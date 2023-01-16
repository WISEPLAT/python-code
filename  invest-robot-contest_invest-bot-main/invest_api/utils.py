import uuid
from decimal import Decimal

from tinkoff.invest import MoneyValue, Quotation, Candle, HistoricCandle
from tinkoff.invest.utils import quotation_to_decimal, decimal_to_quotation

__all__ = ()


def rub_currency_name() -> str:
    return "rub"


def moex_exchange_name() -> str:
    return "MOEX"


def moneyvalue_to_decimal(money_value: MoneyValue) -> Decimal:
    return quotation_to_decimal(
        Quotation(
            units=money_value.units,
            nano=money_value.nano
        )
    )


def decimal_to_moneyvalue(decimal: Decimal, currency: str = rub_currency_name()) -> MoneyValue:
    quotation = decimal_to_quotation(decimal)
    return MoneyValue(
        currency=currency,
        units=quotation.units,
        nano=quotation.nano
    )


def generate_order_id() -> str:
    return str(uuid.uuid4())


def candle_to_historiccandle(candle: Candle) -> HistoricCandle:
    return HistoricCandle(
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        volume=candle.volume,
        time=candle.time,
        is_complete=True
    )
