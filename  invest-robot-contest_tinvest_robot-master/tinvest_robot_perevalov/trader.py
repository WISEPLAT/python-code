import os
from uuid import uuid4

from tinkoff.invest import Client
from tinkoff.invest import schemas

from tinvest_robot_perevalov import _db
from tinvest_robot_perevalov._config import _IS_SANDBOX, app_name, USD_FIGI, CLASS_CODE_SPB, FEE

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)



def _quotation_to_float(q: schemas.Quotation) -> float:
    """Convert quotation to float

    Args:
        q (schemas.Quotation): Quotation value to convert

    Returns:
        float: converted float number
    """
    return float(str(q.units) + '.' + str(q.nano))


def _float_to_quotation(f: float) -> schemas.Quotation:
    """Convert float to quotation

    Args:
        f (float): Float number to convert

    Returns:
        schemas.Quotation: converted quotation number
    """
    return schemas.Quotation(units=int(str(f).split('.')[0]), nano=int(str(f).split('.')[1][:10]))


def _post_order(figi: str, quantity: int, price: schemas.Quotation, direction: schemas.OrderDirection, account_id: str, order_type: schemas.OrderType, news_id: int) -> schemas.PostOrderResponse:
    """Posts order to Tinkoff API

    Args:
        figi (str): FIGI of share
        quantity (int): quantity of share
        price (schemas.Quotation): price of share
        direction (schemas.OrderDirection): order direction (SELL or BUY)
        account_id (str): account ID for order
        order_type (schemas.OrderType): type of order (MARKET or LIMIT)
        news_id (int): ID of news which caused order

    Returns:
        schemas.PostOrderResponse: response from Tinkoff API or None
    """

    with Client(token=os.environ["TINVEST_TOKEN"], app_name=app_name) as client:
        order_id = str(uuid4())
        if _IS_SANDBOX:
            response = client.sandbox.post_sandbox_order(figi=figi, quantity=quantity, direction=direction, account_id=account_id, order_type=order_type, order_id=order_id)
        else:
            response = client.orders.post_order(figi=figi, quantity=quantity, direction=direction, account_id=account_id, order_type=order_type, order_id=order_id)
        _db.put_order_in_db(figi=figi, quantity=quantity, price=_quotation_to_float(response.initial_order_price_pt), direction=int(direction), account_id=account_id, order_type=int(order_type), order_id=order_id, news_id=news_id)
    return response


def _get_shares_by(tickers: list) -> list:
    """Get list of shares by tickers

    Args:
        tickers (list): Tickers of shares

    Returns:
        list: share objects
    """
    shares = list()
    with Client(token=os.environ["TINVEST_TOKEN"], app_name=app_name) as client:
        for ticker in tickers:
            try:
                share = client.instruments.share_by(id_type=schemas.InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=CLASS_CODE_SPB, id=ticker).instrument
                shares.append(share)
            except Exception as e:
                logger.error(str(e))
    return shares


def _get_position_by(positions: list, figi: str) -> schemas.PortfolioPosition:
    """Searches for position by its figi

    Args:
        positions (list): list of positions (or any assets)
        figi (str): figi of position to search for

    Returns:
        schemas.PortfolioPosition: position object or None
    """
    for p in positions:
        if p.figi == figi:
            return p
    return None


def _get_best_price(share: object, direction: object) -> float:
    """Get best price for share from order book (for BUY orders take the first ask, for SELL orders take the first bid)

    Args:
        share (object): share or asset to get price for
        direction (object): direction of order (BUY or SELL)

    Returns:
        float: best price for share or 0.0 if no orders in order book
    """
    try:
        with Client(token=os.environ["TINVEST_TOKEN"], app_name=app_name) as client:
            order_book = client.market_data.get_order_book(figi=share.figi, depth=1)
            if direction == schemas.OrderDirection.ORDER_DIRECTION_BUY:
                return _quotation_to_float(order_book.asks[0].price)
            elif direction == schemas.OrderDirection.ORDER_DIRECTION_SELL:
                return _quotation_to_float(order_book.bids[0].price)
    except Exception as e:
        logger.error(str(e) + " Maybe order book is empty")
        return 0.0

def _get_balance(account_id: str, figi: str = USD_FIGI) -> float:
    """Get balance for account according to FIGI

    Args:
        account_id (str): account id to get balance for
        figi (str, optional): FIGI for getting balance. Defaults to USD_FIGI.

    Returns:
        float: float number of balance
    """
    with Client(token=os.environ["TINVEST_TOKEN"], app_name=app_name) as client:
        if _IS_SANDBOX:
            portfolio = client.sandbox.get_sandbox_portfolio(account_id=account_id)
            position = _get_position_by(portfolio.positions, USD_FIGI)
            return _quotation_to_float(position.quantity)
        else:
            portfolio = client.operations.get_portfolio(account_id=account_id)
            position = _get_position_by(portfolio.positions, USD_FIGI)
            return _quotation_to_float(position.quantity)


def _get_position_from_account(share: object, account_id: str) -> schemas.PortfolioPosition:
    """Get position from account

    Args:
        share (object): a particular share to get position for
        account_id (str): Account ID to get position for

    Returns:
        float: found position or None
    """
    with Client(token=os.environ["TINVEST_TOKEN"], app_name=app_name) as client:
        if _IS_SANDBOX:
            portfolio = client.sandbox.get_sandbox_portfolio(account_id=account_id)
            position = _get_position_by(portfolio.positions, share.figi)
            return position
        else:
            portfolio = client.operations.get_portfolio(account_id=account_id)
            position = _get_position_by(portfolio.positions, share.figi)
            return position


def _get_current_order(share: object, account_id: str) -> schemas.Order:
    """Get current order for share from account

    Args:
        share (object): A particular share to get current order for
        account_id (str): An account ID to get current order for

    Returns:
        schemas.Order: an order object or None
    """
    with Client(token=os.environ["TINVEST_TOKEN"], app_name=app_name) as client:
        if _IS_SANDBOX:
            orders = client.sandbox.get_sandbox_orders(account_id=account_id)
            order = _get_position_by(orders.orders, share.figi)
            return order
        else:
            orders = client.orders.get_orders(account_id=account_id)
            order = _get_position_by(orders.orders, share.figi)
            return order


def _handle_match(sentiment: str, share: object, account_id: str, news_id: int, quantity: int = 1) -> schemas.PostOrderResponse:
    """Handles occurence of an asset name in the news according to sentiment

    Args:
        sentiment (str): Sentiment class of the news
        share (object): A particular share to handle match for
        account_id (str): An account ID to handle match for
        news_id (int): ID of the news which triggered the match
        quantity (int, optional): A quantity of shares to buy (Selling all always). Defaults to 1.

    Returns:
        schemas.PostOrderResponse: Response from Tinkoff API or None if no order placed
    """
    
    logger.info("Handling match for {}".format(share.name))

    response = None
    order = _get_current_order(share, account_id)
    if order:
        logger.warning("There is already an order for {}".format(share.name))
        return response

    if sentiment == 'positive':
        balance = _get_balance(account_id)
        price = _get_best_price(share, schemas.OrderDirection.ORDER_DIRECTION_BUY)
        
        if price == 0.0: # no orders in order book
            return response

        if balance*(1 + FEE) > price: # if we have enough money to buy
            response = _post_order(share.figi, 1, _float_to_quotation(price), schemas.OrderDirection.ORDER_DIRECTION_BUY, account_id, schemas.OrderType.ORDER_TYPE_MARKET, news_id)

    elif sentiment == 'negative':
        position = _get_position_from_account(share, account_id)
        if position: # if we have a position in our portfolio
            price = _get_best_price(share, schemas.OrderDirection.ORDER_DIRECTION_SELL)

            if price == 0.0: # no orders in order book
                return response

            response = _post_order(share.figi, quantity, _float_to_quotation(price), schemas.OrderDirection.ORDER_DIRECTION_SELL, account_id, schemas.OrderType.ORDER_TYPE_MARKET, news_id)
    
    return response


def trade(tickers: list, account_id: str):
    """Main function for searching occurrences of assets in the news and trading them

    Args:
        tickers (list): Tickers to search for
        account_id (str): Account ID to trade with
    """
    news = _db.select_not_checked()
    shares = _get_shares_by(tickers)

    for n in news:
        for share in shares:
            if share.name.lower() in n['title'].lower(): # just dummy check, should be more accurate
                try:
                    _handle_match(sentiment=n['sentiment'], share=share, account_id=account_id, news_id=n['news_id'])
                except Exception as e:
                    logger.error(str(e))
            _db.update_is_checked(n['news_id'])

            