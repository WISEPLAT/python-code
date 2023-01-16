import logging
import uuid

from api_calls.common_requests import make_api_request

orders_path = "tinkoff.public.invest.api.contract.v1.OrdersService/"


def prod_place_order(account_id, figi, quantity, deal_type):
    if deal_type == 'buy':
        direction = "ORDER_DIRECTION_BUY"
    elif deal_type == 'sell':
        direction = "ORDER_DIRECTION_SELL"
    else:
        return

    data = {
        "figi": figi,
        "quantity": quantity,
        "direction": direction,
        "accountId": account_id,
        "orderType": "ORDER_TYPE_MARKET",
        "orderId": str(uuid.uuid4())
    }
    res = make_api_request(orders_path + 'PostOrder', data)
    logging.debug("Prod place order: {}".format(res))
    return res


def prod_get_order_state(account_id, order_id):
    data = {
        "accountId": account_id,
        "orderId": order_id
    }
    res = make_api_request(orders_path + 'GetOrderState', data)
    logging.debug("Sandbox order state: {}".format(res))
    return res


def prod_cancel_order(account_id, order_id):
    data = {
        "accountId": account_id,
        "orderId": order_id
    }
    res = make_api_request(orders_path + 'CancelOrder', data)
    logging.debug("Sandbox cancel order: {}".format(res))
    return res
