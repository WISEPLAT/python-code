from dataclasses import dataclass, field

__all__ = ("StrategySettings", "AccountSettings", "ShareSettings", "TradingSettings", "BlogSettings")


@dataclass(eq=False, repr=True)
class StrategySettings:
    name: str = ""
    figi: str = ""
    ticker: str = ""
    max_lots_per_order: int = 1
    # All internal strategy settings are represented as dict. A strategy class have to parse it himself.
    # Here, we avoid any strong dependencies and obligations
    settings: dict = field(default_factory=dict)
    lot_size: int = 1
    short_enabled_flag: bool = True


@dataclass(eq=False, repr=True)
class AccountSettings:
    min_liquid_portfolio: int = 10000
    min_rub_on_account: int = 5000


@dataclass(eq=False, repr=True)
class ShareSettings:
    ticker: str = ""
    lot: int = 1
    short_enabled_flag: bool = False
    otc_flag: bool = False
    buy_available_flag: bool = False
    sell_available_flag: bool = False
    api_trade_available_flag: bool = False


@dataclass(eq=False, repr=True)
class TradingSettings:
    delay_start_after_open: int = 10
    stop_trade_before_close: int = 300
    stop_signals_before_close: int = 60


@dataclass(eq=False, repr=True)
class BlogSettings:
    blog_status: bool
    bot_token: str
    chat_id: str
