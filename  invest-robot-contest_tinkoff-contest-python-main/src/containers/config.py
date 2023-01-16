import datetime
import re
from dataclasses import dataclass

from tinkoff.invest import CandleInterval

from src.service.errors import ConfigError


@dataclass
class TraderConfig:
    # TODO:
    """Common context of the trader"""

    account_id: str
    instrument_figi: str
    config: dict

    @property
    def candle_timedelta(self) -> datetime.timedelta:
        match = re.match(r"^(?P<number>\d+)(?P<interval>[mhd])$", self.config["window_size"])
        if match is None:
            raise ConfigError("Invalid window_size")
        kwarg_name = {
            "m": "minutes",
            "h": "hours",
            "d": "days",
        }[match.groupdict()["interval"]]
        kwarg_value = int(match.groupdict()["number"])
        return datetime.timedelta(**{kwarg_name: kwarg_value})

    @property
    def candle_interval(self) -> CandleInterval:
        return {
            "1m": CandleInterval.CANDLE_INTERVAL_1_MIN,
            "5m": CandleInterval.CANDLE_INTERVAL_5_MIN,
            "15m": CandleInterval.CANDLE_INTERVAL_15_MIN,
            "1h": CandleInterval.CANDLE_INTERVAL_HOUR,
            "1d": CandleInterval.CANDLE_INTERVAL_DAY,
        }[self.config["candle_interval"]]
