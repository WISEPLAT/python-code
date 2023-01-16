from collections import defaultdict
from order.Orders import Order
from stock.Stock import Stock


class OrderStorage:
    # Instance for storage all orders
    _orders = None
    _orders_archive = []

    @classmethod
    def get_order_storage(cls):
        if cls._orders is None:
            cls._orders = OrderStorage()
        return cls._orders

    def __init__(self):
        self._orders = defaultdict(set)

    def add_order(self, order_id, lots_requested, stock: Stock, order_type):
        self._orders[stock.ticker].add(Order(order_id, lots_requested, order_type))
        self._orders_archive.append(self._orders[stock.ticker])
        return self

    def free_stock_orders(self,stock):
        if stock.ticker in self._orders:
            del self._orders[stock.ticker]
        return self

    def get_order_by_ticker(self, ticker):
        return self._orders[ticker]

    @property
    def orders(self):
        return self._orders

    def __iter__(self):
        self.__storage_keys = list(self._orders.keys())
        self.__iter_pos = 0
        return self

    def __next__(self):
        if self.__iter_pos < len(self.__storage_keys):
            key = self.__storage_keys[self.__iter_pos]
            self.__iter_pos += 1
            return self._orders[key]
        else:
            raise StopIteration
