from account.Account import Account
from tinkoff.invest.services import (OrderType, MoneyValue)
from logger.LoggerFactory import LoggerFactory
from logger.BusinessLogger import BusinessLogger


class SandBoxAccount(Account):
    """ ToDo implement logic for sandbox """

    def __init__(self, client, account_id=None):
        super(SandBoxAccount, self).__init__(client=client, account_id=account_id)

    def get_user_account_id(self):
        """
        Get SandBox Account ID
        """
        sandbox_account_id = self._client.sandbox.open_sandbox_account().account_id
        self._client.sandbox.sandbox_pay_in(account_id=sandbox_account_id,
                                            amount=MoneyValue(currency='rub', units=int(self.daily_limit), nano=0))
        return sandbox_account_id, 'SandBox_Account'

    def _post_order(self, stock, quantity, direction):
        """ Post order into TF platform """
        post_order = self._client.sandbox.post_sandbox_order(figi=stock.figi, quantity=quantity, price=None,
                                                             direction=direction, account_id=self._account_id,
                                                             order_type=OrderType.ORDER_TYPE_MARKET,
                                                             order_id=self.__generate_order_id(ticker=stock.ticker))
        # Log data
        LoggerFactory.get_business_logger_instance().add_event(event_type=BusinessLogger.ORDER_POSTED,
                                                               obj=stock, value=post_order)
        return post_order

    def get_order_from_platform(self, order):
        """ Read detail of order from TF platform """
        order_state = self._client.sandbox.get_sandbox_order_state(account_id=self._account_id,
                                                                   order_id=order.order_id)
        return order_state

    def get_operations(self, from_, to):
        return self.client.sandbox.get_sandbox_operations(account_id=self.account_id,
                                                          from_=from_,
                                                          to=to)
