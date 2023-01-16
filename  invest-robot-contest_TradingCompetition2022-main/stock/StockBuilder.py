from stock.Stock import Stock
from logger.LoggerFactory import LoggerFactory
from logger.BusinessLogger import BusinessLogger
from models.ModelBuilder import ModelBuilder
from tinkoff.invest import InstrumentIdType, RequestError
from order.OrderStorage import OrderStorage

class StockBuilder:
    @classmethod
    def buildStock(cls, ticker, model_name, config, client) -> Stock:
        stock = Stock(ticker)
        stock.logger = LoggerFactory.get_business_logger_instance()
        stock.model = ModelBuilder.buildModel(model_name, stock.ticker, config)
        stock.model_name = model_name
        stock.config = config

        if stock:
            try:
                instrument = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                         class_code='TQBR', id=stock.ticker).instrument
                stock.figi = instrument.figi
                stock.count_in_lot = instrument.lot
            except RequestError as error:
                # Log tech error
                LoggerFactory.get_tech_logger_instance().add_except(error)
        return stock

    @classmethod
    def re_init_stock(cls, stock: Stock, client):
        new_stock = cls.buildStock(ticker=stock.ticker, model_name=stock.model_name,
                                   config=stock.config, client=client)
        order_storage = OrderStorage.get_order_storage()
        order_storage.free_stock_orders(stock)

        # Log data
        LoggerFactory.get_business_logger_instance().add_event(BusinessLogger.STOCK_RE_INIT,
                                                               new_stock, new_stock.model)
        return new_stock
