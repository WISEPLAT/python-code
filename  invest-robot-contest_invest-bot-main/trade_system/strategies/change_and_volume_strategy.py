import logging
from decimal import Decimal
from typing import Optional

from tinkoff.invest import HistoricCandle
from tinkoff.invest.utils import quotation_to_decimal

from configuration.settings import StrategySettings
from trade_system.signal import Signal, SignalType
from trade_system.strategies.base_strategy import IStrategy

__all__ = ("ChangeAndVolumeStrategy")

logger = logging.getLogger(__name__)


class ChangeAndVolumeStrategy(IStrategy):
    """
    Example of trade strategy.
    IMPORTANT: DO NOT USE IT FOR REAL TRADING!
    """
    # Consts for read and parse dict with strategy configuration

    __SIGNAL_VOLUME_NAME = "SIGNAL_VOLUME"
    __SIGNAL_MIN_CANDLES_NAME = "SIGNAL_MIN_CANDLES"
    __LONG_TAKE_NAME = "LONG_TAKE"
    __LONG_STOP_NAME = "LONG_STOP"
    __SHORT_TAKE_NAME = "SHORT_TAKE"
    __SHORT_STOP_NAME = "SHORT_STOP"
    __SIGNAL_MIN_TAIL_NAME = "SIGNAL_MIN_TAIL"

    def __init__(self, settings: StrategySettings) -> None:
        self.__settings = settings

        self.__signal_volume = int(settings.settings[self.__SIGNAL_VOLUME_NAME])
        self.__signal_min_candles = int(settings.settings[self.__SIGNAL_MIN_CANDLES_NAME])
        self.__signal_min_tail = Decimal(settings.settings[self.__SIGNAL_MIN_TAIL_NAME])

        self.__long_take = Decimal(settings.settings[self.__LONG_TAKE_NAME])
        self.__long_stop = Decimal(settings.settings[self.__LONG_STOP_NAME])

        self.__short_take = Decimal(settings.settings[self.__SHORT_TAKE_NAME])
        self.__short_stop = Decimal(settings.settings[self.__SHORT_STOP_NAME])

        self.__recent_candles = []

    @property
    def settings(self) -> StrategySettings:
        return self.__settings

    def update_lot_count(self, lot: int) -> None:
        self.__settings.lot_size = lot

    def update_short_status(self, status: bool) -> None:
        self.__settings.short_enabled_flag = status

    def analyze_candles(self, candles: list[HistoricCandle]) -> Optional[Signal]:
        """
        The method analyzes candles and returns his decision.
        """
        logger.debug(f"Start analyze candles for {self.settings.figi} strategy {__name__}. "
                     f"Candles count: {len(candles)}")

        if not self.__update_recent_candles(candles):
            return None

        if self.__is_match_long():
            logger.info(f"Signal (LONG) {self.settings.figi} has been found.")
            return self.__make_signal(SignalType.LONG, self.__long_take, self.__long_stop)

        if self.settings.short_enabled_flag and self.__is_match_short():
            logger.info(f"Signal (SHORT) {self.settings.figi} has been found.")
            return self.__make_signal(SignalType.SHORT, self.__short_take, self.__short_stop)

        return None

    def __update_recent_candles(self, candles: list[HistoricCandle]) -> bool:
        self.__recent_candles.extend(candles)

        if len(self.__recent_candles) < self.__signal_min_candles:
            logger.debug(f"Candles in cache are low than required")
            return False

        sorted(self.__recent_candles, key=lambda x: x.time)

        # keep only __signal_min_candles candles in cache
        if len(self.__recent_candles) > self.__signal_min_candles:
            self.__recent_candles = self.__recent_candles[len(self.__recent_candles) - self.__signal_min_candles:]

        return True

    def __is_match_long(self) -> bool:
        """
        Check for LONG signal. All candles in cache:
        Green candle, tail lower than __signal_min_tail, volume more that __signal_volume
        """
        for candle in self.__recent_candles:
            logger.debug(f"Recent Candle to analyze {self.settings.figi} LONG: {candle}")
            open_, high, close, low = quotation_to_decimal(candle.open), quotation_to_decimal(candle.high), \
                                      quotation_to_decimal(candle.close), quotation_to_decimal(candle.low)

            if open_ < close \
                    and ((high - close) / (high - low)) <= self.__signal_min_tail \
                    and candle.volume >= self.__signal_volume:
                logger.debug(f"Continue analyze {self.settings.figi}")
                continue

            logger.debug(f"Break analyze {self.settings.figi}")
            break
        else:
            logger.debug(f"Signal detected {self.settings.figi}")
            return True

        return False

    def __is_match_short(self) -> bool:
        """
        Check for LONG signal. All candles in cache:
        Red candle, tail lower than __signal_min_tail, volume more that __signal_volume
        """
        for candle in self.__recent_candles:
            logger.debug(f"Recent Candle to analyze {self.settings.figi} SHORT: {candle}")
            open_, high, close, low = quotation_to_decimal(candle.open), quotation_to_decimal(candle.high), \
                                      quotation_to_decimal(candle.close), quotation_to_decimal(candle.low)

            if open_ > close \
                    and ((close - low) / (high - low)) <= self.__signal_min_tail \
                    and candle.volume >= self.__signal_volume:
                logger.debug(f"Continue analyze {self.settings.figi}")
                continue

            logger.debug(f"Break analyze {self.settings.figi}")
            break
        else:
            logger.debug(f"Signal detected {self.settings.figi}")
            return True

        return False

    def __make_signal(
            self,
            signal_type: SignalType,
            profit_multy: Decimal,
            stop_multy: Decimal
    ) -> Signal:
        # take and stop based on configuration by close price level (close for last price)
        last_candle = self.__recent_candles[len(self.__recent_candles) - 1]

        signal = Signal(
            figi=self.settings.figi,
            signal_type=signal_type,
            take_profit_level=quotation_to_decimal(last_candle.close) * profit_multy,
            stop_loss_level=quotation_to_decimal(last_candle.close) * stop_multy
        )

        logger.info(f"Make Signal: {signal}")

        return signal
