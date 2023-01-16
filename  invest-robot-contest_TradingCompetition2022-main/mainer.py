import configparser
import keyTool
from account.AccountBuilder import AccountBuilder
from stock.StockStorage import StockStorage
from session.Session import Session
from tinkoff.invest import Client
from report.Report import ReportBuilder


def main():
    """ Start Trading (MAIN point)"""
    # Load config and keys
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_token = keyTool.readKeys(config)
    app_name = config.get(section='main', option='app_name')

    # Market Session
    with Client(api_token, app_name=app_name) as client:
        # account for trading
        account = AccountBuilder.build_account(client, config)
        # Create and storage all stock instance for trading """
        stock_storage = StockStorage.collect_stock(client, config, StockStorage())
        # Session for trading
        session = Session.get_session(account, stock_storage)
        # Subscribe to market data
        session.subscribe_last_price()
        # Trading loop (receive market data and do trading)
        session.trading_loop()
        # Get result of session

        session_result = session.get_session_result()
        report = ReportBuilder.buildSessionResultReport(report_name=session.session_id,
                                                        report_source=session_result)
        report.save_to_pdf(file_name=session.session_id)


if __name__ == '__main__':
    main()
