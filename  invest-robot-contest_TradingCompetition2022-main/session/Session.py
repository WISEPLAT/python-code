from tinkoff.invest.services import MarketDataStreamManager
from tinkoff.invest import (
    MarketDataRequest,
    SubscribeLastPriceRequest,
    SubscriptionAction,
    LastPriceInstrument,
    InstrumentIdType,
    OperationType,
    RequestError,
    SecurityTradingStatus
)

from datetime import date, datetime, timedelta
from decimal import Decimal
from account.Account import Account
from stock.StockStorage import StockStorage
from stock.StockBuilder import StockBuilder
from stock.Stock import Stock
from order.OrderStorage import OrderStorage, Order
import time
from logger.LoggerFactory import tech_log, LoggerFactory
from logger.BusinessLogger import BusinessLogger
from session.SessionCache import SessionCache


class Session:
    """ Class to work with market session """

    _session = None

    @classmethod
    def get_session(cls, account, stock_storage):
        """ Get session (singleton) """
        if cls._session is None:
            cls._session = Session(account, stock_storage)

        return cls._session

    def __init__(self, account: Account, stock_storage: StockStorage):
        self._account = account
        self._stock_storage: StockStorage = stock_storage
        self._market_data_stream: MarketDataStreamManager = self._account.client.create_market_data_stream()
        self._session_date = date.today()
        self._session_id = str(datetime.today().now())
        self._stream_limit = 200  # ToDo read from TF platform
        self._stream_count = 0
        self._session_cache = SessionCache.get_session_cache()

    @property
    def session_id(self):
        return self._session_id

    @tech_log
    def trading_loop(self):
        """ Trading LOOP
        Waiting for new last price and do action
        """
        for market_data in self._market_data_stream:
            self.stream_line_process(market_data)

    def stream_line_process(self, market_data):
        if not market_data.last_price:
            # In ping from server do upd stock object
            for stock in self._stock_storage:
                self._process_in_loop(stock, market_data)

        if market_data.last_price:
            # In last price case Do process Stock object (with upd)
            stock = self._stock_storage.get_stock_by_figi(market_data.last_price.figi)
            if stock:
                # Process with stock in trading loop
                self._process_in_loop(stock, market_data)

        if self._stock_storage.is_empty:
            # In case when Stock storage is empty -> Done! Stop
            self._market_data_stream.stop()

    def _process_in_loop(self, stock, market_data):
        """ Process with stock object in trading loop
        """
        if self.is_stock_available_in_session(stock) is True:
            # set last price into model
            if market_data.last_price:
                stock.model.set_last_price(last_price=Account.convert(market_data.last_price.price))
        else:
            # Stock is not available in this session.
            # If time is comme Kill Stock

            self._del_from_session(stock)
            return

        # Update orders result
        if stock:
            self._account.do_upd_order_result(stock)

        if stock:
            # Set order action (if necessary)
            self._do_order_action(stock)

            if self._is_ready_to_del_from_session(stock):
                # If time is comme Kill Stock
                self._del_from_session(stock)
                return

        if stock:
            # ToDo Refactor this
            if stock.is_trading_done is True:
                # re init
                new_stock = StockBuilder().re_init_stock(stock=stock, client=self._account.client)
                self._stock_storage.delete(stock)
                self._stock_storage.add(new_stock)

    def _is_ready_to_del_from_session(self, stock) -> bool:
        """ Check stock can be used or time to delete from this session """
        # if stock.is_trading_done is True or self.is_stock_available_in_session(stock) is False:
        if self.is_stock_available_in_session(stock) is False:
            return True
        else:
            return False

    def _del_from_session(self, stock: Stock):
        # If trading is done or Stock is not available in this session,
        # and We don't have any Non-completed order delete stock from storage
        self._stock_storage.delete(stock)
        # self.unsubscribe_last_price(stock.figi) # ToDo Add UnSubscribe

        # Log data
        LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.STOCK_DEL_FROM_SESS, stock, stock)
        del stock

    @tech_log
    def _do_order_action(self, stock):
        """ Order Action
        """
        # ToDo move this method into right Class (maybe account class is better place for this method)
        match True:
            case stock.model.is_ready_to_open_long:
                # Check is it enough money for buy?
                if self._account.is_ready_to_buy(stock) is True:
                    self._account.set_order(order_type=Account.LONG, stock=stock, quantity=stock.model.possible_lot)

            case stock.model.is_ready_to_close_long:
                if self._account.is_ready_to_sell(stock) is True:
                    self._account.set_order(order_type=Account.CLOSE_LONG, stock=stock, quantity=stock.lot_available)

            case stock.model.is_ready_to_close_short:
                # ToDo Implement Short orders
                # self._account.set_order(account.CLOSE_SHORT)
                pass

            case stock.model.is_ready_to_open_short:
                # ToDo Implement Short orders
                # self._account.set_order(account.SHORT)
                pass

    def is_stock_available_in_session(self, stock: Stock) -> bool:
        """ Is stock available in current session for trading?"""
        # ToDo Add other status too (not only normal trading)
        # ToDo Redefine this check. It is too expensive to ask platform every time

        # Read from cache
        curr_sock_status = self._session_cache.get_cached(group_key=SessionCache.STOCK_AVAILABLE, key=stock.ticker)
        if curr_sock_status is None:
            try:
                curr_sock_status = self._account.client.instruments.share_by(
                    id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                    class_code='TQBR',
                    id=stock.ticker).instrument.trading_status
                # Save to cache
                self._session_cache.cache_data(group=SessionCache.STOCK_AVAILABLE,
                                               key=stock.ticker, data=curr_sock_status)
            except RequestError as error:
                # Log tech error
                LoggerFactory.get_tech_logger_instance().add_except(error)
                return True  # ToDo Workaround

        if SecurityTradingStatus:
            if curr_sock_status == SecurityTradingStatus.SECURITY_TRADING_STATUS_NORMAL_TRADING:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def is_stock_open_in_order(stock) -> bool:
        """ Check this stock has opened order """
        order_storage: OrderStorage = OrderStorage.get_order_storage()
        for order in order_storage.get_order_by_ticker(stock.ticker):
            if order.is_order_completed is False:
                return False
        return True

    def subscribe_last_price(self) -> MarketDataStreamManager:
        """ Subscribe to last price (Market Data)"""
        sub_last_price = SubscribeLastPriceRequest()
        sub_last_price.subscription_action = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE
        sub_last_price.instruments = []
        for i in self._stock_storage.get_all_figis():
            sub_last_price.instruments.append(LastPriceInstrument(figi=i))
        try:
            self._market_data_stream.subscribe(MarketDataRequest(subscribe_last_price_request=sub_last_price))
        except RequestError as error:
            LoggerFactory.get_tech_logger_instance().add_except(error)
        return self._market_data_stream

    def unsubscribe_last_price(self, figi):
        """ UnSubscribe from last price (Market Data)"""
        # ToDo On Platform TF UnSubscribe is not work correct - need to check
        sub_last_price = SubscribeLastPriceRequest()
        sub_last_price.subscription_action = SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE
        sub_last_price.instruments = [LastPriceInstrument(figi=figi)]
        self._market_data_stream.unsubscribe(MarketDataRequest(subscribe_last_price_request=sub_last_price))
        return self._market_data_stream

    def get_session_result(self):
        """
        Receive result of Session (result of trading)
        :return:
        """
        result = dict(count_long_opened=0, count_long_closed=0, count_orders=0,
                      fee=list(), sum_fee=Decimal(), buy=list(), sell=list())

        from_ = datetime.today() - timedelta(days=1)
        to = datetime.today()

        count_long_opened = 0
        count_long_closed = 0
        for order in OrderStorage():
            if order.order_type == Order.TYPE_LONG_OPEN:
                count_long_opened += 1
            if order.order_type == Order.TYPE_LONG_CLOSE:
                count_long_closed += 1
        count_orders = count_long_opened + count_long_closed
        operations = self._account.get_operations(from_=from_, to=to)
        result['count_long_opened'] = count_long_opened
        result['count_long_closed'] = count_long_closed
        result['count_orders'] = count_orders

        def __get_dict_operation(name, operation):
            return dict(name=name, payment=Account.convert(operation.payment),
                        currency=operation.currency, quantity=operation.quantity)

        figi = dict()
        for i in operations.operations:
            instrument = None
            if i.figi:
                if i.figi not in figi:
                    try:
                        instrument = self._account.client.instruments.share_by(
                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                            class_code='TQBR', id=i.figi).instrument
                        figi[i.figi] = instrument
                    except RequestError as error:
                        # Tech log
                        LoggerFactory.get_tech_logger_instance().add_except(error)
                        continue
                else:
                    instrument = figi[i.figi]

            if i.operation_type == OperationType.OPERATION_TYPE_BROKER_FEE:
                # Collect FEE result
                result['fee'].append(Account.convert(i.payment))
                result['sum_fee'] += Account.convert(i.payment)

            if instrument:
                if i.operation_type == OperationType.OPERATION_TYPE_BUY:
                    # Collect all BUY operation
                    result['buy'].append(__get_dict_operation(instrument.name, i))

                elif i.operation_type == OperationType.OPERATION_TYPE_SELL:
                    # Collect all SELL operation
                    result['sell'].append(__get_dict_operation(instrument.name, i))
        return result

    def _check_stream_limit(self):
        """ Check if limit of stream grader then profile limit, wait a minute """
        # ToDo it is workaround, It should be changed
        if self._stream_count > (self._stream_limit - 10):
            time.sleep(60)
            self._stream_count = 0
        self._stream_count += 1
