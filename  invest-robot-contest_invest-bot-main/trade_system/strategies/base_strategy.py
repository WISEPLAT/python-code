import abc
import logging
from typing import Optional

from tinkoff.invest import HistoricCandle

from configuration.settings import StrategySettings
from trade_system.signal import Signal

__all__ = ("IStrategy")

logger = logging.getLogger(__name__)


class IStrategy(abc.ABC):
    @property
    @abc.abstractmethod
    def settings(self) -> StrategySettings:
        pass

    @abc.abstractmethod
    def analyze_candles(self, candles: list[HistoricCandle]) -> Optional[Signal]:
        pass

    @abc.abstractmethod
    def update_lot_count(self, lot: int) -> None:
        pass

    @abc.abstractmethod
    def update_short_status(self, status: bool) -> None:
        pass
