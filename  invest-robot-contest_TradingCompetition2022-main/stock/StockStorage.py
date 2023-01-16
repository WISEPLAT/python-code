from stock.Stock import Stock
from collections import defaultdict
from stock.StockBuilder import StockBuilder
from tinkoff.invest import InstrumentIdType, RequestError
from logger.LoggerFactory import LoggerFactory
from logger.BusinessLogger import BusinessLogger


class StockStorage:
    """
    Class for storage all stock instance
    """

    @staticmethod
    def collect_stock(client, config, stock_storage):
        """ Create instance of stock, set FIGI from market and save instance into Storage
        """
        # List of tickers for trading
        tickers_name = config.get(section='TradingStrategy', option='ticker_list').split(',')
        # Model name for trading
        model_name = config.get(section='TradingStrategy', option='model')  # Trading model name
        for ticker_name in tickers_name:
            stock: Stock = StockBuilder.buildStock(ticker=ticker_name, model_name=model_name,
                                                   config=config, client=client)
            if stock:
                stock_storage.add(stock)
                # Log data
                LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.STOCK_IN_WORK, stock)

        return stock_storage

    def __init__(self):
        self._storage = defaultdict(Stock)

    ''' { Iteration for stock in Storage '''

    def __iter__(self):
        self._iteration_cursor = 0
        self._iteration_keys = list(self._storage.keys())
        return self

    def __next__(self):
        if self._iteration_cursor < len(self._iteration_keys):
            stock = self._storage[self._iteration_keys[self._iteration_cursor]]
            self._iteration_cursor += 1
            return stock
        else:
            raise StopIteration

    ''' Iteration for stock in Storage } '''

    def add(self, stock: Stock):
        self._storage[stock.ticker] = stock

    def delete(self, stock: Stock) -> Stock:
        stock = self._storage[stock.ticker]
        del self._storage[stock.ticker]
        return stock

    def get_stock(self, ticker):
        return self._storage[ticker]

    def get_all_figis(self):
        figis = set()
        for stock in self:
            figis.add(stock.figi)
        return figis

    def get_stock_by_figi(self, figi) -> Stock:
        # ToDo Do optimize, figi should be dict key as ticker
        for stock in self:
            if stock.figi == figi:
                return stock

    @property
    def is_empty(self):
        return True if len(self._storage) == 0 else False
