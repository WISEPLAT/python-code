import logging

from api_calls.common_requests import make_api_request
from utils.util import pretty_dict


def get_prod_accounts():
    res = make_api_request('tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts')
    logging.debug(pretty_dict(res))
    return res


def get_prod_portfolio(account_id):
    res = make_api_request('tinkoff.public.invest.api.contract.v1.OperationsService/GetPortfolio', {
        'accountId': account_id
    })
    logging.debug("Prod portfolio for AccountId = '{}':\n{}".format(account_id, pretty_dict(res)))
    return res


def get_prod_positions(account_id):
    res = make_api_request('tinkoff.public.invest.api.contract.v1.OperationsService/GetPositions', {
        'accountId': account_id
    })
    logging.debug("Prod positions for AccountId = '{}':\n{}".format(account_id, pretty_dict(res)))
    return res
