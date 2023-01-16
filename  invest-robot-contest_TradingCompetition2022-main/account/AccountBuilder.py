from account.Account import Account
from account.SandboxAccount import SandBoxAccount
from decimal import Decimal
from logger.LoggerFactory import LoggerFactory
from logger.BusinessLogger import BusinessLogger


class AccountBuilder:

    @classmethod
    def build_account(cls, client, config):
        combat_mode = True if config.get(section='main', option='combat_mode') == 'True' else False
        account_id = config.get(section='main', option='account')
        daily_limit = config.get(section='TradingStrategy', option='daily_limit')
        daily_drop_limit = config.get(section='TradingStrategy', option='daily_drop_limit')
        if combat_mode is True:
            # combat_mode Account class
            account = Account(client=client, account_id=account_id)
        else:
            # Sandbox version of account class
            account = SandBoxAccount(client=client, account_id=account_id)
        account.set_daily_limit(Decimal(daily_limit))
        account.set_daily_drop_limit(Decimal(daily_drop_limit))
        # Log data
        LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.ACCOUNT_STARTED, account, account)
        return account
