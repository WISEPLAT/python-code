from configparser import ConfigParser

from configuration.settings import StrategySettings, AccountSettings, TradingSettings, BlogSettings

__all__ = ("ProgramConfiguration")


class ProgramConfiguration:
    """
    Represent all bot configuration
    """
    def __init__(self, file_name: str) -> None:
        # classic ini file
        config = ConfigParser()
        config.read(file_name)

        self.__tinkoff_token = config["INVEST_API"]["TOKEN"]
        self.__tinkoff_app_name = config["INVEST_API"]["APP_NAME"]

        self.__blog_settings = BlogSettings(
            blog_status=bool(int(config["BLOG"]["STATUS"])),
            bot_token=config["BLOG"]["TELEGRAM_BOT_TOKEN"],
            chat_id=config["BLOG"]["TELEGRAM_CHAT_ID"]
        )

        self.__account_settings = AccountSettings(
            min_liquid_portfolio=int(config["TRADING_ACCOUNT"]["MIN_LIQUID_PORTFOLIO"]),
            min_rub_on_account=int(config["TRADING_ACCOUNT"]["MIN_RUB_ON_ACCOUNT"])
        )

        self.__trading_settings = TradingSettings(
            delay_start_after_open=int(config["TRADING_SETTINGS"]["DELAY_START_AFTER_EXCHANGE_OPEN_SECONDS"]),
            stop_trade_before_close=int(config["TRADING_SETTINGS"]["STOP_TRADE_BEFORE_EXCHANGE_CLOSE_SECONDS"]),
            stop_signals_before_close=int(config["TRADING_SETTINGS"]["STOP_SIGNALS_BEFORE_EXCHANGE_CLOSE_MINUTES"])
        )

        self.__trade_strategy_settings = []
        for strategy_section in config.sections():
            if strategy_section.startswith("STRATEGY_") and not strategy_section.endswith("_SETTINGS"):
                self.__trade_strategy_settings.append(
                    StrategySettings(
                        name=config[strategy_section]["STRATEGY_NAME"],
                        figi=config[strategy_section]["FIGI"],
                        ticker=config[strategy_section]["TICKER"],
                        max_lots_per_order=int(config[strategy_section]["MAX_LOTS_PER_ORDER"]),
                        settings=config[strategy_section + "_SETTINGS"]
                    )
                )

    @property
    def tinkoff_token(self) -> str:
        return self.__tinkoff_token

    @property
    def tinkoff_app_name(self) -> str:
        return self.__tinkoff_app_name

    @property
    def blog_settings(self) -> BlogSettings:
        return self.__blog_settings

    @property
    def account_settings(self) -> AccountSettings:
        return self.__account_settings

    @property
    def trade_strategy_settings(self) -> list[StrategySettings]:
        return self.__trade_strategy_settings

    @property
    def trading_settings(self) -> TradingSettings:
        return self.__trading_settings
