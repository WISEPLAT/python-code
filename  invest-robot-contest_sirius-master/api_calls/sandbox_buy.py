import logging

from api_calls.common_requests import make_api_request

sandbox_service_path = "tinkoff.public.invest.api.contract.v1.SandboxService/"


def sandbox_place_order(account_id, figi, quantity, deal_type):
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
        "orderId": ""
    }
    res = make_api_request(sandbox_service_path + 'PostSandboxOrder', data)
    logging.debug("Sandbox place order: {}".format(res))
    return res


def sandbox_get_order_state(account_id, order_id):
    data = {
        "accountId": account_id,
        "orderId": order_id
    }
    res = make_api_request(sandbox_service_path + 'GetSandboxOrderState', data)
    logging.debug("Sandbox order state: {}".format(res))
    return res


def sandbox_cancel_order(account_id, order_id):
    data = {
        "accountId": account_id,
        "orderId": order_id
    }
    res = make_api_request(sandbox_service_path + 'CancelSandboxOrder', data)
    logging.debug("Sandbox cancel order: {}".format(res))
    return res
