from tinkoff.invest.services import (Services, OrderDirection, OrderType, MoneyValue)
from tinkoff.invest.schemas import (AccountStatus, AccessLevel)
from tinkoff.invest.exceptions import RequestError

from order.Orders import Order
from order.OrderStorage import OrderStorage
from stock.Stock import Stock
import decimal
from decimal import Decimal
from logger.LoggerFactory import tech_log, LoggerFactory
from logger.BusinessLogger import BusinessLogger
import datetime


class Account:
    """
    Client account. Implemented all manipulation with client (order, close, etc)
    """

    # Order types
    LONG = "long"  # Long order
    SHORT = "short"  # Short order
    CLOSE_LONG = "close_long"  # Close long order (sell stock)
    CLOSE_SHORT = "close_short"  # Close short order (bay stock)

    def __init__(self, client, account_id=None):
        """
        :param client: TF service API object
        :param account_id: TF account ID
        """
        self._client: Services = client
        self._order_storage: OrderStorage = OrderStorage.get_order_storage()
        self._daily_limit: Decimal = Decimal()
        self._daily_drop_limit: Decimal = Decimal()
        self._account_balance: Decimal = Decimal()

        # account id from input constructor input or from used account (TF)
        self._account_id, self._account_name = account_id if account_id else self.get_user_account_id()
        self.id = self._account_id

        self._orders = dict()

    @property
    def account_balance(self):
        try:
            total_amount_currencies = self.client.operations.get_portfolio(account_id=self.account_id). \
                total_amount_currencies
            self._account_balance = Decimal('.'.join((str(total_amount_currencies.units),
                                                      str(total_amount_currencies.nano))))
            return self._account_balance
        except RequestError:
            print("error to get account balance")
            pass  # ToDo add log
        return None

    @property
    def client(self) -> Services:
        return self._client

    @property
    def account_id(self):
        return self._account_id

    def get_user_account_id(self):
        """ Get first correct available user account id """
        try:
            for i in self._client.users.get_accounts().accounts:
                if i.status == AccountStatus.ACCOUNT_STATUS_OPEN and \
                        i.access_level == AccessLevel.ACCOUNT_ACCESS_LEVEL_FULL_ACCESS:
                    return i.id, i.name
        except RequestError as error:
            logger = LoggerFactory().get_tech_logger_instance()
            logger.add_except(error)

    def __generate_order_id(self, ticker):
        """ Generate unique order ID"""
        return ticker + str(len(self._order_storage.orders[ticker]) + 1) + str(datetime.datetime.now())

    def set_daily_limit(self, daily_limit: Decimal):
        self._daily_limit = daily_limit
        return self

    @property
    def daily_limit(self):
        return self._daily_limit

    def set_daily_drop_limit(self, daily_drop_limit):
        self._daily_drop_limit = daily_drop_limit
        return self

    @tech_log
    def set_order(self, order_type, stock, quantity):
        """ Set order in market
        """
        try:
            match order_type:
                case self.LONG:  # Set Open long order
                    post_order = self._open_long_order(stock, quantity)
                    if post_order:
                        # Add Order to storage
                        self._order_storage.add_order(post_order.order_id,
                                                      post_order.lots_requested, stock,
                                                      Order.TYPE_LONG_OPEN)
                        # Inform model about opened order
                        stock.model.long_open_ordered()

                case self.CLOSE_LONG:  # Set Close long order
                    post_order = self._close_long_order(stock, quantity)
                    if post_order:
                        # Add Order to storage
                        self._order_storage.add_order(post_order.order_id,
                                                      post_order.lots_requested, stock,
                                                      Order.TYPE_LONG_CLOSE)
                    # Inform model about opened order
                    stock.model.long_close_ordered()

                case self.SHORT:
                    # ToDo
                    # self._open_short_order()
                    pass
                case self.CLOSE_SHORT:
                    # ToDo
                    # self._close_long_order()
                    pass
        except RequestError as error:
            # Log tech error
            LoggerFactory.get_tech_logger_instance().add_except(error)

    def _post_order(self, stock, quantity, direction):
        """ Post order into TF platform """
        post_order = self._client.orders.post_order(figi=stock.figi, quantity=quantity, price=None,
                                                    direction=direction, account_id=self._account_id,
                                                    order_type=OrderType.ORDER_TYPE_MARKET,
                                                    order_id=self.__generate_order_id(ticker=stock.ticker))
        # Log data
        LoggerFactory.get_business_logger_instance().add_event(event_type=BusinessLogger.ORDER_POSTED,
                                                               obj=stock, value=post_order)

        return post_order

    def _open_long_order(self, stock: Stock, quantity):
        """
        Set Open long order
        :param quantity: count of lot
        """
        return self._post_order(stock=stock, quantity=quantity, direction=OrderDirection.ORDER_DIRECTION_BUY)

    def _close_long_order(self, stock: Stock, quantity):
        """ Set Close Long order
        :param quantity: count of lot
        """
        return self._post_order(stock=stock, quantity=quantity, direction=OrderDirection.ORDER_DIRECTION_SELL)

    def get_order_from_platform(self, order):
        """ Read detail of order from TF platform """
        try:
            order_state = self._client.orders.get_order_state(account_id=self._account_id, order_id=order.order_id)
        except RequestError as error:
            # Log tech error
            LoggerFactory.get_tech_logger_instance().add_except(error)
            return None

        return order_state

    def do_upd_order_result(self, stock: Stock):
        """
        Get and update result of order (only for non-completed)
        """
        # ToDo TF has API for select all orders (not one by one) It should be changed (optimize issue)
        # ToDo this method (set_available_lot) CAN'T be use for multi_orders.
        # ToDo It should be changes (it could be + and - operation)
        # ToDo it's work only when all order done.It'll be better to change, it have to increase and decrease every time
        for order in self._order_storage.orders[stock.ticker]:
            if order.order_type == Order.TYPE_LONG_OPEN and stock.model.is_long_open_done is True:
                continue
            if order.order_type == Order.TYPE_LONG_CLOSE and stock.model.is_long_close_done is True:
                continue
            order_state = self.get_order_from_platform(order)
            if order_state is None:
                continue
            if order_state.lots_executed == order_state.lots_requested:
                if order.order_type == Order.TYPE_LONG_OPEN:
                    stock.set_available_lot(order_state.lots_executed)
                    stock.model.set_average_position_price(
                        avg_price=Account.convert(order_state.average_position_price))
                    stock.model.is_long_open_done = True
                    # Log data
                    LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.ORDER_OPEN_LONG_DONE,
                                                                           stock, order_state)

                elif order.order_type == Order.TYPE_LONG_CLOSE:
                    stock.set_available_lot(stock.lot_available - order.lots_executed)
                    stock.model.is_long_close_done = True
                    # Log data
                    LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.ORDER_CLOSE_LONG_DONE,
                                                                               stock, order_state)

    def is_ready_to_buy(self, stock: Stock) -> bool:
        """
        Check can we buy stock in this account
        :param stock: Stock which we want to buy
        """
        account_balance = self.account_balance
        need_money = stock.model.possible_lot * (stock.model.count_in_lot * stock.model.last_price)
        if account_balance:
            if account_balance > need_money:
                return True
            else:
                # not enough money on balance
                # Log data
                LoggerFactory.get_business_logger_instance().add_event_no_money(obj=stock, balance=account_balance,
                                                                                need_money=need_money)

        return False

    @staticmethod
    def is_ready_to_sell(stock: Stock) -> bool:
        """
        Check can we sell stock in this account
        :param stock: Stock which we want to sell
        """
        if stock.lot_available == 0:
            return False
        # ToDo This method check only our session stock but it is better to read available stock from TF platform
        return True

    @classmethod
    def convert(cls, price: MoneyValue):
        """ Convert money to dec """
        return Decimal(price.units + price.nano / 10 ** 9)

    @classmethod
    def convert_out(cls, price):
        """ Convert money to dec """
        return price.quantize(Decimal("1.00"), decimal.ROUND_CEILING)

    def get_operations(self, from_, to):
        return self.client.operations.get_operations(account_id=self.account_id,
                                                     from_=from_,
                                                     to=to)
