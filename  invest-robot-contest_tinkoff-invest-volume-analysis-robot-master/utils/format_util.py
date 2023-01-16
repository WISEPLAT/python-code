from tinkoff.invest import Quotation
from tinkoff.invest.utils import quotation_to_decimal


def quotation_to_float(quotation: Quotation):
    return float(quotation_to_decimal(quotation))


def fixed_float(number: float) -> str:
    return f"{number:.3f}"
